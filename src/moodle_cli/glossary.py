"""Canonical, deterministic evidence semantics for CLI and library consumers.

Notes describe field meaning, not a site's capabilities or a user's permissions.
Keep definitions here; docs, command help and annotated results reuse them.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, TypedDict


class Term(TypedDict):
    definition: str
    limitation: str
    fields: list[str]


def _term(definition: str, limitation: str, *fields: str) -> Term:
    return {"definition": definition, "limitation": limitation, "fields": list(fields)}


TERMS: dict[str, Term] = {
    "response_scope": _term(
        "Results describe records returned for this account, query and retrieval time.",
        "Permissions, visibility, filters and pagination can restrict coverage. An empty result is not proof "
        "of no activity.",
        "data",
        "warnings",
    ),
    "missing_value": _term(
        "Absent, null, empty and zero values have field-specific meanings; some CLI models supply defaults "
        "for absent fields.",
        "Do not turn an unavailable or defaulted value into a measured zero, a failure or proof of never "
        "participating.",
        "null",
        "0",
    ),
    "timestamp": _term(
        "Moodle epoch timestamps are seconds since the Unix epoch; display dates in an explicitly stated timezone.",
        "A zero or missing timestamp is not automatically an event in 1970. Interpret its documented field "
        "sentinel first.",
        "timecreated",
        "timemodified",
        "timestart",
        "timefinish",
    ),
    "date_window": _term(
        "For a consumer using [since, until), since is inclusive and until is exclusive.",
        "This notation does not claim every Moodle API uses it. To include a calendar day, use the next local "
        "midnight as the exclusive end.",
        "since",
        "until",
        "timezone",
    ),
    "snapshot": _term(
        "A snapshot records evidence observed at its collection time; a delta compares two such observations.",
        "A first snapshot has no previous baseline. This does not mean Moodle has no historical timestamps or posts.",
        "as_of",
        "collected_at",
        "delta",
    ),
    "course": _term(
        "A course ID identifies a course on this Moodle site; a course listing is a visibility or enrolment "
        "view of that site.",
        "Listed courses do not establish a teacher role. Names and numeric IDs are not globally unique across sites.",
        "id",
        "courseid",
        "fullname",
        "shortname",
    ),
    "role": _term(
        "Roles are context-scoped assignments; one person may hold multiple roles, including locally defined roles.",
        "A role label is not a complete effective-capability check. Missing roles do not imply student; do "
        "not infer role from course access.",
        "roles",
        "shortname",
        "roleid",
        "contextid",
    ),
    "enrolment": _term(
        "Enrolment links users to courses; enrolledusercount counts enrolled users, not specifically students.",
        "Teachers and other roles may be included. Enrolment is not evidence of attendance, access or completion.",
        "enrolledusercount",
        "userid",
        "courseid",
    ),
    "enrolment_method": _term(
        "An enrolment method describes a course enrolment mechanism and its returned status.",
        "A listed method does not establish that this user is enrolled through it or can self-enrol.",
        "type",
        "status",
        "courseid",
    ),
    "my_course_lastaccess": _term(
        "In enrol.my-courses, lastaccess is the selected user's most recent recorded access to that course.",
        "Null may reflect no recorded access or unavailable visibility. One last-access value cannot "
        "reconstruct visits or frequency.",
        "lastaccess",
    ),
    "roster_lastaccess": _term(
        "In enrol.list-users, lastaccess refers to the site; lastcourseaccess refers to the queried course. "
        "Moodle documents zero as never for these API fields.",
        "Do not substitute site access for course access. Missing or null is not a measured zero; neither "
        "field supplies an access history.",
        "lastaccess",
        "lastcourseaccess",
    ),
    "progress": _term(
        "Course progress and completion reflect Moodle's configured completion tracking.",
        "Unavailable progress is not zero. Progress is not a grade, time spent, or measured learning gain.",
        "progress",
        "completed",
    ),
    "module_identity": _term(
        "cmid or coursemodule identifies the course-module link; an activity instance ID identifies a record "
        "in its module type.",
        "These IDs are not interchangeable. Match the requested ID kind before calling an activity API.",
        "cmid",
        "coursemodule",
        "instance",
        "modname",
        "id",
    ),
    "resource_listing": _term(
        "Activity and resource listings describe available course content and configuration.",
        "Listing a resource or file does not show which students opened it, how often, or for how long.",
        "modules",
        "contents",
        "url",
        "modname",
    ),
    "assignment_due": _term(
        "duedate is a due-date value for the assignment in the returned context; zero normally means no due date set.",
        "Do not declare a learner late without checking applicable extensions, user/group overrides and "
        "submission evidence. Due date is not cut-off date.",
        "duedate",
        "cutoffdate",
        "extensionduedate",
        "allowsubmissionsfromdate",
    ),
    "assignment_status": _term(
        "Submission status new is an initial record, draft is not finally submitted, submitted marks "
        "submission, and reopened denotes another attempt being opened.",
        "Record existence is not a submitted exercise. Moodle can create an empty new record while preparing "
        "a user's status or grade, so its creation or modification time is not learner activity. Current "
        "status is not an event history; group submissions and attempts require their own scope.",
        "status",
        "userid",
        "attemptnumber",
        "groupid",
    ),
    "submission_modified": _term(
        "Submission timemodified is the last modification time of the returned submission record.",
        "It does not establish the original submission time or a complete history of deliveries and resubmissions.",
        "timemodified",
    ),
    "grading_status": _term(
        "gradingstatus describes grading progress for a submission, distinct from its submission status.",
        "Graded does not necessarily mean released to the learner; marking-workflow states and visibility matter.",
        "gradingstatus",
        "workflowstate",
        "grade",
    ),
    "per_user_status": _term(
        "Assignment status is a per-user view; when userid is omitted the API uses the authenticated user.",
        "A teacher's personal submission status is not the course-wide student submission population.",
        "userid",
        "lastattempt",
        "gradingsummary",
    ),
    "grade": _term(
        "A grade belongs to its item, scale, range and aggregation context; displayed grade strings may be formatted.",
        "Null, hidden, ungraded or sentinel values are not automatically zero. A numeric zero may be assigned "
        "without a submitted artifact: it proves neither delivery nor lateness. Do not compare raw grades "
        "across different scales as percentages.",
        "grade",
        "grademin",
        "grademax",
        "feedback",
    ),
    "assignment_grade_configuration": _term(
        "Assignment grade in the assignment listing configures grading: a positive value is a points maximum, "
        "a negative value references a scale, and zero means no grade.",
        "This is not any student's achieved grade.",
        "grade",
    ),
    "forum_identity": _term(
        "For forum.discussions, id is the first/root post ID and discussion is the discussion ID; forum.posts "
        "takes the discussion ID.",
        "Do not pass the root-post ID where a discussion ID is required. Replies take a parent post ID.",
        "id",
        "discussion",
        "discussionid",
        "parentid",
    ),
    "forum_discussion_activity": _term(
        "Discussion created describes creation; timemodified describes discussion modification/activity; "
        "numreplies counts replies rather than the root post.",
        "Modification is not the creation date of every post. numunread is reader-specific, not total participation.",
        "created",
        "timemodified",
        "numreplies",
        "numunread",
        "usermodified",
    ),
    "forum_post": _term(
        "Post timecreated is its creation timestamp; parentid identifies the parent, with no parent for a root post.",
        "Returned posts are accessible surviving content, not proof of all historic posts, views or reads. "
        "Counts alone do not measure contribution quality.",
        "timecreated",
        "parentid",
        "author",
        "discussionid",
    ),
    "activity_completion": _term(
        "Activity completion state: 0 incomplete, 1 complete, 2 complete/pass, 3 complete/fail; tracking: 0 "
        "none, 1 manual, 2 automatic.",
        "Other/version-specific states must not be guessed. Completion reflects configured criteria, not "
        "necessarily a resource view or mastery.",
        "state",
        "tracking",
        "timecompleted",
        "cmid",
    ),
    "course_completion": _term(
        "Course completion reports satisfaction of the configured course-completion criteria for the selected user.",
        "It is distinct from one activity's completion and from a passing final grade; criteria and "
        "processing determine its meaning.",
        "completed",
        "completions",
        "aggregation",
    ),
    "quiz_configuration": _term(
        "Quiz timeopen/timeclose describe configured availability, and grade is the configured maximum grade.",
        "These are not attempt dates or a learner's achieved grade; individual/group overrides may alter availability.",
        "timeopen",
        "timeclose",
        "grade",
        "coursemodule",
    ),
    "quiz_attempt": _term(
        "A quiz attempt has its own ID, attempt number, state, start and finish timestamps.",
        "An unfinished attempt is not a finished failure. Attempt count is not participant count; a missing "
        "grade is not zero.",
        "id",
        "attempt",
        "state",
        "timestart",
        "timefinish",
        "grade",
    ),
    "quiz_best_grade": _term(
        "Best-grade response supplies the user's returned quiz grade together with hasgrade when provided.",
        "Respect hasgrade and the quiz scale; do not infer a zero score when no grade is available.",
        "grade",
        "hasgrade",
    ),
    "calendar": _term(
        "Calendar timestart is an event start and timeduration is a duration in seconds; eventtype identifies "
        "its kind.",
        "Calendar events are not activity logs. Empty calendar results do not prove no submissions, forum "
        "posts or course activity.",
        "timestart",
        "timeduration",
        "eventtype",
        "courseid",
    ),
    "group": _term(
        "Groups contain course participants; groupings collect groups for course activity configuration.",
        "A grouping is not a user roster. Group membership does not establish submission, activity or a teacher role.",
        "id",
        "courseid",
        "groups",
        "groupingid",
    ),
    "cohort": _term(
        "A cohort is a site/category-level collection of users, distinct from a course group.",
        "Cohort membership alone does not establish course enrolment or participation.",
        "id",
        "contextid",
        "idnumber",
    ),
    "choice_result": _term(
        "Choice results describe options and responses made visible by the activity's settings and permissions.",
        "Options are not respondents; multiple selections and hidden responses can prevent interpreting "
        "option totals as unique students.",
        "options",
        "userresponses",
        "users",
        "countanswers",
    ),
    "feedback": _term(
        "Feedback analysis summarizes visible survey responses; anonymous indicates the activity's anonymity setting.",
        "Do not deanonymize responses or infer named respondents from aggregates. Non-response is not proof "
        "of inactivity elsewhere.",
        "anonymous",
        "itemsdata",
        "completedcount",
        "users",
    ),
    "badge": _term(
        "A returned badge is an award with an issuance date and issuer, optionally associated with a course.",
        "Issuance date is not necessarily the date of the underlying learning activity; a badge is not an "
        "access history.",
        "dateissued",
        "issuername",
        "courseid",
    ),
    "message": _term(
        "Messages and unread counts belong to the requested user/conversation and its visibility and read state.",
        "Unread is not evidence that a learner ignored course content; messaging is distinct from forum participation.",
        "useridfrom",
        "useridto",
        "timecreated",
        "read",
        "unreadcount",
    ),
    "file": _term(
        "File metadata describes a stored file and its Moodle file-area/context location.",
        "A file listing is not a download log. Access URLs may require authentication and should not expose tokens.",
        "filename",
        "fileurl",
        "contextid",
        "component",
        "filearea",
        "itemid",
    ),
    "workshop": _term(
        "Workshop submissions and grades belong to the peer-assessment activity; submission and assessment "
        "grades are distinct.",
        "Do not interpret a workshop grade as an assignment submission grade or an unqualified final course grade.",
        "grade",
        "gradinggrade",
        "authorid",
        "timecreated",
        "timemodified",
    ),
    "activity_entry": _term(
        "Glossary/database entries and wiki/lesson pages are activity content records; creation and "
        "modification concern those records.",
        "Retrieving content does not establish views or unique participants. A current page is not a full "
        "revision history.",
        "id",
        "timecreated",
        "timemodified",
        "content",
    ),
    "site_function": _term(
        "Advertised web-service functions describe what the connected token's service exposes.",
        "Advertisement is not a guarantee of permission for every course or user. Missing or denied APIs are "
        "not empty datasets.",
        "functions",
        "name",
        "userid",
    ),
    "user_identity": _term(
        "A user ID identifies an account on this Moodle site; returned profiles expose only selected permitted fields.",
        "An account is not necessarily a student. A profile lookup does not establish course role or access history.",
        "id",
        "userid",
        "fullname",
        "email",
    ),
    "note": _term(
        "Course notes are access-controlled annotations with their own author, subject and publication context.",
        "Notes are not a learner activity log or objective measures of achievement.",
        "content",
        "userid",
        "publishstate",
    ),
}


# Explicit coverage, including offline commands with no evidence notes. No wildcard
# inference from ambiguous field names (notably lastaccess, grade and timemodified).
COMMAND_TERMS: dict[str, tuple[str, ...]] = {
    "auth.status": (),
    "auth.profiles": (),
    "content.types": (),
    "assign.list": ("module_identity", "assignment_due", "assignment_grade_configuration"),
    "assign.submissions": ("assignment_status", "submission_modified", "grading_status", "timestamp"),
    "assign.status": (
        "per_user_status",
        "assignment_status",
        "submission_modified",
        "assignment_due",
        "grading_status",
    ),
    "assign.grades": ("grade", "grading_status"),
    "assign.grade": ("grade", "grading_status"),
    "enrol.my-courses": ("course", "enrolment", "my_course_lastaccess", "progress"),
    "enrol.list-users": ("enrolment", "role", "roster_lastaccess", "group"),
    "enrol.methods": ("enrolment_method",),
    "course.list": ("course",),
    "course.get": ("course",),
    "course.search": ("course",),
    "course.timeline": ("course", "progress"),
    "course.categories": ("course",),
    "course.contents": ("module_identity", "resource_listing"),
    "course.module": ("module_identity", "resource_listing"),
    "content.list": ("module_identity", "resource_listing"),
    "forum.list": ("module_identity", "response_scope"),
    "forum.discussions": ("forum_identity", "forum_discussion_activity", "timestamp"),
    "forum.posts": ("forum_post", "timestamp"),
    "forum.post": ("forum_identity",),
    "forum.reply": ("forum_identity",),
    "completion.status": ("module_identity", "activity_completion"),
    "completion.course": ("course_completion",),
    "completion.update": ("activity_completion",),
    "quiz.list": ("module_identity", "quiz_configuration"),
    "quiz.attempts": ("quiz_attempt", "timestamp"),
    "quiz.review": ("quiz_attempt", "grade"),
    "quiz.best-grade": ("quiz_best_grade",),
    "calendar.events": ("calendar", "timestamp"),
    "calendar.upcoming": ("calendar", "timestamp"),
    "calendar.course": ("calendar", "timestamp"),
    "calendar.create": ("calendar", "timestamp"),
    "grade.get": ("grade",),
    "grade.report": ("grade",),
    "grade.overview": ("grade",),
    "grade.table": ("grade",),
    "group.list": ("group",),
    "group.groupings": ("group",),
    "group.user-groups": ("group",),
    "cohort.list": ("cohort",),
    "cohort.create": ("cohort",),
    "cohort.add-members": ("cohort",),
    "cohort.remove-members": ("cohort",),
    "choice.list": ("module_identity",),
    "choice.results": ("choice_result",),
    "feedback.list": ("module_identity", "feedback"),
    "feedback.analysis": ("feedback",),
    "feedback.non-respondents": ("feedback",),
    "badge.user": ("badge", "timestamp"),
    "message.list": ("message",),
    "message.conversations": ("message",),
    "message.unread": ("message",),
    "message.send": ("message",),
    "file.list": ("file",),
    "file.upload": ("file",),
    "workshop.submissions": ("workshop",),
    "workshop.grades": ("workshop", "grade"),
    "glossary.entries": ("activity_entry",),
    "database.entries": ("activity_entry",),
    "wiki.pages": ("activity_entry",),
    "wiki.page": ("activity_entry",),
    "lesson.pages": ("activity_entry",),
    "site.info": ("site_function", "user_identity"),
    "site.functions": ("site_function",),
    "user.me": ("user_identity",),
    "user.list": ("user_identity",),
    "user.get": ("user_identity",),
    "user.profiles": ("user_identity",),
    "role.assign": ("role",),
    "role.unassign": ("role",),
    "note.course": ("note",),
}


def glossary_terms() -> dict[str, Term]:
    """Return an independent copy of the full canonical glossary."""
    return deepcopy(TERMS)


def terms_for_command(command_key: str) -> dict[str, Term]:
    """Select notes by CLI command identity, never by guessing raw field meaning."""
    key = ".".join(command_key.strip().split()).replace("_", "-")
    ids = COMMAND_TERMS.get(key, ())
    if not ids:
        return {}
    ids = tuple(dict.fromkeys(("response_scope", "missing_value", *ids)))
    return {term_id: deepcopy(TERMS[term_id]) for term_id in ids}


def annotate_result(command_key: str, data: Any) -> dict[str, Any]:
    """Opt-in envelope; never mutate, reinterpret or invent measurements in data."""
    return {"data": data, "field_notes": terms_for_command(command_key)}


def help_for_command(command_key: str) -> str:
    """Offline field guidance for command help, drawn from the same definitions."""
    notes = terms_for_command(command_key)
    return "\n\n".join(f"{key}: {term['definition']} {term['limitation']}" for key, term in notes.items())


def render_markdown() -> str:
    """Generate the public glossary; committed documentation is checked in tests."""
    lines = [
        "# Moodle CLI evidence glossary",
        "",
        "Generated from `moodle_cli.glossary`; edit the canonical definitions, not this file.",
        "",
        "Scope: the standard API command families exposed by this CLI, not every Moodle feature.",
        "Definitions are deterministic metadata, not evidence that a field is present or an API is available.",
        "Notes apply to the returned account, activity and query context. Raw JSON remains unchanged unless "
        "annotation is requested.",
        "",
        "The `date_window` and `snapshot` entries are reusable vocabulary for consumers; they do not add date "
        "filters or snapshot storage to this CLI.",
        "",
        "Validation references: CLI service models; Moodle standard `enrol/externallib.php`, "
        "`mod/assign/externallib.php`,",
        "`mod/forum/externallib.php`, `mod/quiz/externallib.php`, and `lib/completionlib.php`.",
        "Moodle versions, permissions and module configuration can change optional fields and visibility.",
        "",
        "## Usage",
        "",
        "- `moodle terms` lists the full glossary offline; `moodle terms submission_modified` selects a term.",
        "- `moodle terms --command assign.submissions` selects the applicable notes.",
        "- `moodle assign submissions --help` includes the same evidence guidance.",
        "- `moodle --annotated assign submissions 42` returns a `{data, field_notes}` JSON envelope.",
        "- Existing `--json` output is unchanged. `moodle-readonly` supports the same glossary surfaces.",
        "- The Moodle glossary activity remains available as `moodle glossary entries`; it is unrelated to "
        "this terminology command.",
        "",
    ]
    for name, term in TERMS.items():
        lines.extend(
            [
                f"## {name}",
                "",
                term["definition"],
                "",
                f"Limit: {term['limitation']}",
                "",
                "Fields/context: " + ", ".join(f"`{field}`" for field in term["fields"]) + ".",
                "",
            ]
        )
    lines.extend(
        [
            "## Command coverage",
            "",
            "Every mapped evidence command also includes response-scope and missing-value cautions.",
            "",
        ]
    )
    for command, ids in sorted(COMMAND_TERMS.items()):
        lines.append(f"- `{command}`: {', '.join(ids) or 'offline command; no evidence notes'}")
    return "\n".join(lines) + "\n"
