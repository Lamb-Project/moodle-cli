"""The same evidence vocabulary must reach docs, help and annotated responses."""

from pathlib import Path

from moodle_cli.cli.readonly import READONLY_COMMANDS
from moodle_cli.glossary import (
    COMMAND_TERMS,
    TERMS,
    annotate_result,
    glossary_terms,
    help_for_command,
    render_markdown,
    terms_for_command,
)


def test_documentation_is_generated_from_canonical_terms():
    assert (Path(__file__).parents[1] / "docs/glossary.md").read_text() == render_markdown()


def test_all_readonly_command_families_have_explicit_coverage():
    commands = {f"{group}.{cmd}" for group, names in READONLY_COMMANDS.items() for cmd in names}
    assert commands <= COMMAND_TERMS.keys()
    assert all(term in TERMS for ids in COMMAND_TERMS.values() for term in ids)


def test_terms_have_deterministic_definitions_limitations_and_fields():
    assert len(TERMS) >= 35
    for term in TERMS.values():
        assert term["definition"] and term["limitation"] and term["fields"]
        assert set(term) == {"definition", "limitation", "fields"}


def test_assignment_modified_time_not_presented_as_delivery():
    notes = terms_for_command("assign.submissions")
    assert "original submission time" in notes["submission_modified"]["limitation"]
    assert "Record existence is not a submitted exercise" in notes["assignment_status"]["limitation"]
    assert "forum_post" not in notes


def test_numeric_zero_grade_does_not_imply_a_submission():
    note = terms_for_command("assign.grades")["grade"]
    assert "zero may be assigned without a submitted artifact" in note["limitation"]
    assert "neither delivery nor lateness" in note["limitation"]


def test_same_field_name_has_different_contextual_semantics():
    courses = terms_for_command("enrol.my-courses")
    roster = terms_for_command("enrol.list-users")
    assert "my_course_lastaccess" in courses and "roster_lastaccess" not in courses
    assert "roster_lastaccess" in roster and "my_course_lastaccess" not in roster
    assert "site" in roster["roster_lastaccess"]["definition"]
    assert "course" in courses["my_course_lastaccess"]["definition"]
    assert "assignment_grade_configuration" in terms_for_command("assign.list")
    assert "assignment_grade_configuration" not in terms_for_command("assign.grades")


def test_course_listing_does_not_claim_roles_were_returned():
    notes = terms_for_command("enrol.my-courses")
    assert "role" not in notes
    assert "do not establish a teacher role" in notes["course"]["limitation"]


def test_forum_post_creation_is_not_discussion_modification():
    assert "forum_post" in terms_for_command("forum.posts")
    assert "forum_discussion_activity" not in terms_for_command("forum.posts")
    assert "first/root post ID" in terms_for_command("forum.discussions")["forum_identity"]["definition"]


def test_annotated_result_preserves_values_and_has_no_per_row_duplication():
    data = [{"id": 1, "status": "new", "timemodified": 0}, {"id": 2, "timemodified": None}]
    result = annotate_result("assign.submissions", data)
    assert result["data"] is data
    assert result["data"] == data
    assert set(result) == {"data", "field_notes"}
    assert "field_notes" not in data[0]


def test_notes_are_defensive_copies():
    result = terms_for_command("assign.submissions")
    result["submission_modified"]["fields"].append("not_a_real_field")
    assert "not_a_real_field" not in TERMS["submission_modified"]["fields"]
    result = glossary_terms()
    result.clear()
    assert TERMS


def test_unknown_or_offline_commands_do_not_guess_notes():
    assert terms_for_command("unknown.command") == {}
    assert terms_for_command("content.types") == {}
    assert annotate_result("unknown.command", {"timemodified": 123})["field_notes"] == {}


def test_help_and_annotations_use_identical_meanings_and_aliases():
    notes = terms_for_command("enrol.list-users")
    assert notes == terms_for_command("enrol list_users")
    text = help_for_command("enrol.list-users")
    assert all(term["definition"] in text and term["limitation"] in text for term in notes.values())
