"""The read-only security boundary: the Web-Service functions a read-only client may call.

This frozenset IS the boundary enforced by `moodle-readonly`. It was derived by tracing
every CLI command through its service wrapper to the actual ``wsfunction`` it POSTs — the
code, not the command name. A command named ``list`` that calls a write function would be
a write; only the ``wsfunction`` tells the truth. Verified 2026-06-03 against the service
layer (``services/*.py``).

It lives at the client layer (not the CLI layer) on purpose: ``MoodleHTTPClient.call`` is
the single chokepoint every service-based request funnels through, so enforcing here means
even a write command that ever leaked through the CLI-level filter (drift, a future bug)
is still refused at the point of the POST.

NEVER add a ``*_view_*`` function to this set. Moodle's ``_view_`` functions log a view
event server-side and can trigger activity-completion — a write wearing a reader's face.
Adding read functions is a security decision: keep this list reviewed.
"""

from __future__ import annotations

READ_ALLOWLIST: frozenset[str] = frozenset(
    {
        # site / identity
        "core_webservice_get_site_info",
        # courses
        "core_course_get_courses",
        "core_course_search_courses",
        "core_course_get_contents",
        # users
        "core_user_get_users",
        "core_user_get_users_by_field",
        # enrolment
        "core_enrol_get_users_courses",
        "core_enrol_get_enrolled_users",
        # grades (report read only)
        "gradereport_user_get_grade_items",
        # assignments
        "mod_assign_get_assignments",
        "mod_assign_get_submissions",
        # forums
        "mod_forum_get_forums_by_courses",
        "mod_forum_get_forum_discussions",
        # quizzes
        "mod_quiz_get_quizzes_by_courses",
        "mod_quiz_get_user_attempts",
        # calendar
        "core_calendar_get_calendar_events",
        # completion (status read only)
        "core_completion_get_activities_completion_status",
        # cohorts
        "core_cohort_get_cohorts",
        # files (listing only)
        "core_files_get_files",
        # messages
        "core_message_get_messages",
        "core_message_get_conversations",
        "core_message_get_conversation_messages",
    }
)
