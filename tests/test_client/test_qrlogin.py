"""Tests for the QR-login exchange + parsing (client layer)."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from moodle_cli.client.exceptions import AuthenticationError
from moodle_cli.client.qrlogin import (
    MOODLE_APP_USER_AGENT,
    exchange_qr_login,
    parse_moodlemobile_uri,
)

SITE = "https://moodle.example.com"
AJAX = f"{SITE}/lib/ajax/service-nologin.php"


class TestParseUri:
    def test_full_uri(self) -> None:
        url, key, uid = parse_moodlemobile_uri(
            "moodlemobile://https://moodle.example.com?qrlogin=abc123&userid=42"
        )
        assert url == "https://moodle.example.com"
        assert key == "abc123"
        assert uid == "42"

    def test_trailing_slash_stripped(self) -> None:
        url, _, _ = parse_moodlemobile_uri(
            "moodlemobile://https://moodle.example.com/?qrlogin=k&userid=1"
        )
        assert url == "https://moodle.example.com"

    def test_no_query_raises(self) -> None:
        with pytest.raises(AuthenticationError):
            parse_moodlemobile_uri("moodlemobile://https://moodle.example.com")

    def test_missing_key_raises(self) -> None:
        with pytest.raises(AuthenticationError):
            parse_moodlemobile_uri("moodlemobile://https://moodle.example.com?userid=42")


class TestExchange:
    @respx.mock
    def test_success(self) -> None:
        route = respx.post(AJAX).mock(
            return_value=Response(
                200,
                json=[{"error": False, "data": {"token": "TOK", "privatetoken": "PRIV"}}],
            )
        )
        result = exchange_qr_login(SITE, "freshkey", 42)
        assert result["token"] == "TOK"
        assert result["privatetoken"] == "PRIV"
        # The app User-Agent is required by the server; assert we send it.
        assert route.calls.last.request.headers["user-agent"] == MOODLE_APP_USER_AGENT

    @respx.mock
    def test_invalidkey_is_friendly(self) -> None:
        respx.post(AJAX).mock(
            return_value=Response(
                200,
                json=[{"error": True, "exception": {"errorcode": "invalidkey", "message": "Invalid key"}}],
            )
        )
        with pytest.raises(AuthenticationError) as exc:
            exchange_qr_login(SITE, "deadkey", 42)
        assert exc.value.error_code == "invalidkey"
        assert "single-use" in str(exc.value)

    @respx.mock
    def test_no_token_in_data_raises(self) -> None:
        respx.post(AJAX).mock(
            return_value=Response(200, json=[{"error": False, "data": {}}])
        )
        with pytest.raises(AuthenticationError):
            exchange_qr_login(SITE, "k", 42)

    @respx.mock
    def test_unexpected_shape_raises(self) -> None:
        respx.post(AJAX).mock(return_value=Response(200, json={"not": "a list"}))
        with pytest.raises(AuthenticationError):
            exchange_qr_login(SITE, "k", 42)
