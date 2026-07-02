"""Tests for explicit, opt-in trimming (--trim-messages) and the trim() helper.

Background: table renderers used to hard-truncate long text fields (forum posts
at 80 chars, cohort descriptions at 60, …) with no indication that a cut had
happened. An agent reading `forum posts` output took the first 80 chars of a
post for the whole message. The contract now is: full text by default; trimming
only when asked for via --trim-messages N; and a trimmed value always says how
many chars were cut.
"""

from __future__ import annotations

import re

import respx
from click.testing import CliRunner
from httpx import Response

from moodle_cli.cli.main import MoodleContext, cli
from moodle_cli.cli.readonly import cli_readonly
from moodle_cli.client.http import MoodleHTTPClient
from moodle_cli.output import trim

BASE_URL = "https://moodle.example.com"


# ---- trim() helper ----------------------------------------------------------


def test_trim_no_limit_returns_full_text() -> None:
    text = "x" * 5000
    assert trim(text, None) == text


def test_trim_under_limit_untouched() -> None:
    assert trim("short", 80) == "short"


def test_trim_at_limit_untouched() -> None:
    text = "x" * 80
    assert trim(text, 80) == text


def test_trim_over_limit_says_so_with_count() -> None:
    text = "a" * 300
    out = trim(text, 80)
    assert out.startswith("a" * 80)
    assert out.endswith("[… trimmed 220 chars]")


def test_trim_handles_none_and_empty() -> None:
    assert trim(None, 80) == ""
    assert trim("", None) == ""


# ---- option is registered on both binaries ----------------------------------


def test_option_in_moodle_help() -> None:
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "--trim-messages" in result.output


def test_option_in_moodle_readonly_help() -> None:
    result = CliRunner().invoke(cli_readonly, ["--help"])
    assert result.exit_code == 0
    assert "--trim-messages" in result.output


def test_option_rejects_zero_and_negative() -> None:
    for bad in ("0", "-5"):
        result = CliRunner().invoke(cli, ["--trim-messages", bad, "site", "info"])
        assert result.exit_code != 0
        assert "trim-messages" in result.output


# ---- end-to-end through `forum posts` ---------------------------------------

LONG_MESSAGE = "m" * 300

POSTS_RESPONSE = {
    "posts": [
        {
            "id": 1,
            "discussionid": 42,
            "parentid": None,
            "subject": "Long one",
            "message": f"<p>{LONG_MESSAGE}</p>",
            "timecreated": 1780000000,
            "author": {"fullname": "Test Author"},
        }
    ]
}


def _squash(s: str) -> str:
    """Keep only word chars + the trim-marker glyphs, so wrapped Rich table cells
    (which interleave newlines and box-drawing borders) compare as one string."""
    return re.sub(r"[^0-9A-Za-z…\[\]]+", "", s)


def _invoke_posts(monkeypatch, args: list[str], entry=cli):  # type: ignore[no-untyped-def]
    def fake_get_client(self: MoodleContext) -> MoodleHTTPClient:
        return MoodleHTTPClient(base_url=BASE_URL, token="t")

    monkeypatch.setattr(MoodleContext, "get_client", fake_get_client)
    with respx.mock(assert_all_called=False) as router:
        router.post(f"{BASE_URL}/webservice/rest/server.php").mock(
            return_value=Response(200, json=POSTS_RESPONSE)
        )
        return CliRunner().invoke(entry, args)


def test_forum_posts_full_text_by_default(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    result = _invoke_posts(monkeypatch, ["forum", "posts", "42"])
    assert result.exit_code == 0, result.output
    assert LONG_MESSAGE in _squash(result.output)
    assert "trimmed" not in result.output


def test_forum_posts_trim_is_explicit(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    result = _invoke_posts(monkeypatch, ["--trim-messages", "40", "forum", "posts", "42"])
    assert result.exit_code == 0, result.output
    squashed = _squash(result.output)
    assert "m" * 40 in squashed
    assert LONG_MESSAGE not in squashed
    # the cut is announced, with the exact number of chars removed (300 - 40)
    assert "trimmed260chars" in squashed.replace("…", "").replace("[", "").replace("]", "")


def test_forum_posts_trim_on_readonly_binary(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    result = _invoke_posts(
        monkeypatch, ["--trim-messages", "40", "forum", "posts", "42"], entry=cli_readonly
    )
    assert result.exit_code == 0, result.output
    assert "trimmed" in result.output


def test_forum_posts_json_never_trimmed(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    result = _invoke_posts(
        monkeypatch, ["--json", "--trim-messages", "40", "forum", "posts", "42"]
    )
    assert result.exit_code == 0, result.output
    assert LONG_MESSAGE in result.output
    assert "trimmed" not in result.output
