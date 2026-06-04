"""Tests for moodle-readonly — the read-only CLI and its enforced boundary.

These tests guard a security boundary, so they are deliberately strict:
- the WS allowlist may not contain anything write-shaped,
- the command manifest may not drift from the real CLI,
- no write command may be reachable,
- the client must refuse a non-allowlisted wsfunction before it hits the network.
"""

from __future__ import annotations

import pytest
import respx
from click.testing import CliRunner
from httpx import Response

from moodle_cli.cli.main import cli
from moodle_cli.cli.readonly import READONLY_COMMANDS, cli_readonly
from moodle_cli.client.exceptions import ReadOnlyViolation
from moodle_cli.client.http import MoodleHTTPClient
from moodle_cli.client.readonly import READ_ALLOWLIST

BASE_URL = "https://moodle.example.com"
TOKEN = "test-token"

# Write verbs that do NOT collide with Moodle module names (unlike "_assign_" /
# "_enrol_", which are the assign/enrol *modules*, whose _get_ functions are reads).
# "_view_" is included: it logs a view event server-side and can trigger completion.
WRITE_FRAGMENTS = ("_create_", "_update_", "_delete_", "_save_", "_send_", "_view_")


class TestReadAllowlist:
    def test_allowlist_functions_are_read_shaped(self) -> None:
        # Every read WS function names its action as get/search.
        not_read = [f for f in READ_ALLOWLIST if "_get_" not in f and "_search_" not in f]
        assert not_read == [], f"non-read-shaped functions in allowlist: {not_read}"

    def test_allowlist_has_no_write_verbs(self) -> None:
        offenders = [f for f in READ_ALLOWLIST if any(w in f for w in WRITE_FRAGMENTS)]
        assert offenders == [], f"write-verb functions in read allowlist: {offenders}"

    def test_allowlist_is_nonempty_frozenset(self) -> None:
        assert isinstance(READ_ALLOWLIST, frozenset)
        assert len(READ_ALLOWLIST) >= 20

    def test_reviewed_denylist_is_disjoint_from_allowlist(self) -> None:
        # The dangerous read-SHAPED functions (token/key issuers, draft allocators,
        # the wiki edit-lock) must never leak into the allowlist. The allowlist's
        # "_get_ means read" test cannot catch these, so guard them explicitly.
        from moodle_cli.client.readonly import READ_DENYLIST_REVIEWED

        leaked = READ_ALLOWLIST & READ_DENYLIST_REVIEWED
        assert leaked == frozenset(), f"reviewed-unsafe functions in allowlist: {leaked}"

    def test_content_map_matches_allowlist(self) -> None:
        # Every wsfunction the content dispatcher can call must be allowlisted,
        # or moodle-readonly would refuse it at the chokepoint.
        from moodle_cli.services.content import CONTENT_FUNCTIONS

        for _type, (fn, _key) in CONTENT_FUNCTIONS.items():
            assert fn in READ_ALLOWLIST, f"content function not allowlisted: {fn}"


class TestManifestIntegrity:
    """The command manifest must name only commands that actually exist (no drift)."""

    def test_every_manifest_command_exists_in_full_cli(self) -> None:
        for gname, subs in READONLY_COMMANDS.items():
            group = cli.commands.get(gname)
            assert group is not None, f"manifest names unknown group '{gname}'"
            real = set(group.commands)  # type: ignore[attr-defined]
            missing = subs - real
            assert not missing, f"group '{gname}' manifest names missing commands: {missing}"

    def test_call_and_role_excluded(self) -> None:
        assert "call" not in READONLY_COMMANDS
        assert "role" not in READONLY_COMMANDS


class TestReadonlyCliSurface:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_help_ok_and_branded(self) -> None:
        result = self.runner.invoke(cli_readonly, ["--help"])
        assert result.exit_code == 0
        assert "read-only" in result.output.lower()

    def test_no_call_escape_hatch(self) -> None:
        result = self.runner.invoke(cli_readonly, ["call", "core_user_create_users"])
        assert result.exit_code != 0  # command does not exist here

    def test_no_role_group(self) -> None:
        result = self.runner.invoke(cli_readonly, ["role", "--help"])
        assert result.exit_code != 0

    def test_write_subcommands_absent(self) -> None:
        # (group, write-subcommand) pairs that must NOT be reachable
        forbidden = [
            ("assign", "grade"),
            ("course", "create"), ("course", "update"), ("course", "delete"),
            ("user", "create"), ("user", "update"), ("user", "delete"),
            ("message", "send"),
            ("calendar", "create"),
            ("completion", "update"),
            ("cohort", "create"), ("cohort", "delete"),
            ("cohort", "add-members"), ("cohort", "remove-members"),
            ("file", "upload"),
            ("forum", "post"),
            ("auth", "login"), ("auth", "logout"),
        ]
        for gname, sub in forbidden:
            group = cli_readonly.commands.get(gname)
            present = group is not None and sub in group.commands  # type: ignore[attr-defined]
            assert not present, f"write command reachable in readonly: {gname} {sub}"

    def test_read_subcommands_present(self) -> None:
        for gname, sub in [
            ("course", "list"), ("assign", "submissions"),
            ("grade", "report"), ("site", "info"), ("user", "me"),
            # comprehensive additions
            ("forum", "posts"), ("enrol", "methods"), ("grade", "overview"),
            ("calendar", "upcoming"), ("group", "list"), ("feedback", "analysis"),
            ("content", "list"), ("badge", "user"), ("completion", "course"),
            # ws-coverage-gap additions
            ("calendar", "course"), ("course", "timeline"), ("note", "course"),
            ("quiz", "review"), ("workshop", "grades"), ("glossary", "entries"),
            ("wiki", "page"), ("lesson", "pages"), ("database", "entries"),
        ]:
            group = cli_readonly.commands.get(gname)
            assert group is not None and sub in group.commands  # type: ignore[attr-defined]


class TestClientBoundary:
    @respx.mock
    def test_readonly_client_allows_read_function(self) -> None:
        respx.post(f"{BASE_URL}/webservice/rest/server.php").mock(
            return_value=Response(200, json=[{"id": 1}])
        )
        client = MoodleHTTPClient(base_url=BASE_URL, token=TOKEN, readonly=True)
        assert client.call("core_course_get_courses") == [{"id": 1}]

    def test_readonly_client_refuses_write_function_before_network(self) -> None:
        # No respx mock: if the guard fails to short-circuit, the POST would error
        # differently — so a clean ReadOnlyViolation proves we never hit the network.
        client = MoodleHTTPClient(base_url=BASE_URL, token=TOKEN, readonly=True)
        with pytest.raises(ReadOnlyViolation, match="mod_assign_save_grade"):
            client.call("mod_assign_save_grade", assignmentid=1)

    @respx.mock
    def test_non_readonly_client_unrestricted(self) -> None:
        respx.post(f"{BASE_URL}/webservice/rest/server.php").mock(
            return_value=Response(200, json={"ok": True})
        )
        client = MoodleHTTPClient(base_url=BASE_URL, token=TOKEN)  # readonly=False
        assert client.call("mod_assign_save_grade") == {"ok": True}
