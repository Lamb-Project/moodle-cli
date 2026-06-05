"""Tests for the `auth qr-login` CLI command (isolated from real config/keyring)."""

from __future__ import annotations

from pathlib import Path

import pytest
import respx
from click.testing import CliRunner
from httpx import Response

from moodle_cli.cli.main import cli

SITE = "https://moodle.example.com"
AJAX = f"{SITE}/lib/ajax/service-nologin.php"
REST = f"{SITE}/webservice/rest/server.php"


@pytest.fixture
def isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Redirect config to a tmp file and the keyring to an in-memory dict."""
    from moodle_cli.config import auth as authmod
    from moodle_cli.config import manager as mgr

    monkeypatch.setattr(mgr, "DEFAULT_CONFIG_FILE", tmp_path / "config.toml")

    store: dict[tuple[str, str], str] = {}

    class FakeKeyring:
        class errors:  # noqa: N801 - mimic keyring.errors namespace
            class PasswordDeleteError(Exception):
                pass

        def set_password(self, service: str, key: str, value: str) -> None:
            store[(service, key)] = value

        def get_password(self, service: str, key: str) -> str | None:
            return store.get((service, key))

        def delete_password(self, service: str, key: str) -> None:
            store.pop((service, key), None)

    monkeypatch.setattr(authmod, "keyring", FakeKeyring())


@respx.mock
def test_qr_login_with_uri(isolated: None) -> None:
    respx.post(AJAX).mock(
        return_value=Response(200, json=[{"error": False, "data": {"token": "TOK"}}])
    )
    respx.post(REST).mock(
        return_value=Response(200, json={"username": "marc.alier", "sitename": "Demo", "release": "4.5"})
    )
    result = CliRunner().invoke(
        cli,
        [
            "auth", "qr-login",
            "moodlemobile://https://moodle.example.com?qrlogin=freshkey&userid=42",
            "--name", "demo",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Logged in as marc.alier" in result.output
    assert "Demo" in result.output


@respx.mock
def test_qr_login_expired_key(isolated: None) -> None:
    respx.post(AJAX).mock(
        return_value=Response(
            200,
            json=[{"error": True, "exception": {"errorcode": "invalidkey", "message": "Invalid key"}}],
        )
    )
    result = CliRunner().invoke(
        cli,
        [
            "auth", "qr-login",
            "moodlemobile://https://moodle.example.com?qrlogin=dead&userid=42",
            "--name", "demo",
        ],
    )
    assert result.exit_code == 1
    assert "single-use" in result.output


def test_qr_login_requires_input(isolated: None) -> None:
    result = CliRunner().invoke(cli, ["auth", "qr-login"])
    assert result.exit_code != 0
    assert "Provide the QR" in result.output


@respx.mock
def test_qr_login_username_override_skips_siteinfo(isolated: None) -> None:
    # No REST mock registered: passing --username must avoid the site-info call.
    respx.post(AJAX).mock(
        return_value=Response(200, json=[{"error": False, "data": {"token": "TOK"}}])
    )
    result = CliRunner().invoke(
        cli,
        [
            "auth", "qr-login",
            "--url", SITE, "--key", "k", "--userid", "42",
            "--username", "preset",
            "--name", "demo",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Logged in as preset" in result.output
