"""Glossary discovery and additive output must work without a Moodle account."""

import json

import pytest
from click.testing import CliRunner

from moodle_cli.cli.main import MoodleContext, cli
from moodle_cli.cli.readonly import READONLY_COMMANDS, cli_readonly
from moodle_cli.glossary import TERMS, terms_for_command
from moodle_cli.services.assign import AssignService


@pytest.fixture(autouse=True)
def no_auth(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("offline documentation attempted authentication")
    monkeypatch.setattr(MoodleContext, "get_client", forbidden)


@pytest.mark.parametrize("root", [cli, cli_readonly])
def test_offline_terms(root):
    result = CliRunner().invoke(root, ["--json", "terms"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == TERMS
    name = next(iter(TERMS))
    result = CliRunner().invoke(root, ["--json", "terms", name])
    assert json.loads(result.output) == {name: TERMS[name]}
    result = CliRunner().invoke(root, ["terms", "--command", "assign.submissions"])
    assert result.exit_code == 0, result.output
    assert "Limitation:" in result.output


@pytest.mark.parametrize("root", [cli, cli_readonly])
@pytest.mark.parametrize("args", [["terms", "unknown-term"], ["terms", "--command", "unknown.command"]])
def test_unknown_terms_are_explicit(root, args):
    result = CliRunner().invoke(root, args)
    assert result.exit_code == 2
    assert "Unknown term" in result.output or "No glossary terms" in result.output


@pytest.mark.parametrize("root", [cli, cli_readonly])
def test_command_help_uses_canonical_notes(root):
    result = CliRunner().invoke(root, ["assign", "submissions", "--help"], terminal_width=240)
    assert result.exit_code == 0, result.output
    assert "Field meanings and limitations" in result.output
    normalized = " ".join(result.output.split())
    for entry in terms_for_command("assign.submissions").values():
        assert " ".join(entry["definition"].split()) in normalized


def test_metadata_command_is_not_a_moodle_service():
    assert "terms" not in READONLY_COMMANDS
    assert "entries" in cli_readonly.commands["glossary"].commands


@pytest.mark.parametrize("root", [cli, cli_readonly])
def test_annotation_is_opt_in_and_raw_shape_unchanged(root, monkeypatch):
    data = [{"assignment": 7, "userid": 8, "grade": "5.00"}]
    monkeypatch.setattr(MoodleContext, "get_client", lambda self: object())
    monkeypatch.setattr(AssignService, "get_grades", lambda self, ids: data)
    runner = CliRunner()
    raw = runner.invoke(root, ["--json", "assign", "grades", "7"])
    assert raw.exit_code == 0, raw.output
    assert json.loads(raw.output) == data
    annotated = runner.invoke(root, ["--annotated", "assign", "grades", "7"])
    assert annotated.exit_code == 0, annotated.output
    envelope = json.loads(annotated.output)
    assert set(envelope) == {"data", "field_notes"}
    assert envelope["data"] == data
    assert envelope["field_notes"]
    raw_again = runner.invoke(root, ["--json", "assign", "grades", "7"])
    assert raw_again.output == raw.output


def test_annotation_does_not_enable_writes():
    result = CliRunner().invoke(cli_readonly, ["--annotated", "assign", "grade"])
    assert result.exit_code == 2
    assert "No such command" in result.output
