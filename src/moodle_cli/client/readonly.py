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
        "core_course_get_categories",
        "core_course_get_course_module",
        # users
        "core_user_get_users",
        "core_user_get_users_by_field",
        "core_user_get_course_user_profiles",
        # enrolment
        "core_enrol_get_users_courses",
        "core_enrol_get_enrolled_users",
        "core_enrol_get_course_enrolment_methods",
        # groups
        "core_group_get_course_groups",
        "core_group_get_course_groupings",
        "core_group_get_course_user_groups",
        # grades (report read only)
        "gradereport_user_get_grade_items",
        "gradereport_overview_get_course_grades",
        "gradereport_user_get_grades_table",
        # assignments
        "mod_assign_get_assignments",
        "mod_assign_get_submissions",
        "mod_assign_get_grades",
        "mod_assign_get_submission_status",
        # forums
        "mod_forum_get_forums_by_courses",
        "mod_forum_get_forum_discussions",
        "mod_forum_get_discussion_posts",
        # quizzes
        "mod_quiz_get_quizzes_by_courses",
        "mod_quiz_get_user_attempts",
        "mod_quiz_get_user_best_grade",
        # calendar
        "core_calendar_get_calendar_events",
        "core_calendar_get_action_events_by_timesort",
        # completion (status read only)
        "core_completion_get_activities_completion_status",
        "core_completion_get_course_completion_status",
        # cohorts
        "core_cohort_get_cohorts",
        # files (listing only)
        "core_files_get_files",
        # messages
        "core_message_get_messages",
        "core_message_get_conversations",
        "core_message_get_conversation_messages",
        "core_message_get_unread_conversations_count",
        # badges
        "core_badges_get_user_badges",
        # feedback (survey) module — read views of activities + aggregate analysis
        "mod_feedback_get_feedbacks_by_courses",
        "mod_feedback_get_analysis",
        "mod_feedback_get_non_respondents",
        # choice module
        "mod_choice_get_choices_by_courses",
        "mod_choice_get_choice_results",
        # activity-content listers (one per standard module type; see services/content.py).
        # Every one is a pure `_get_..._by_courses` lister — no view event, no mutation.
        "mod_resource_get_resources_by_courses",
        "mod_page_get_pages_by_courses",
        "mod_url_get_urls_by_courses",
        "mod_book_get_books_by_courses",
        "mod_folder_get_folders_by_courses",
        "mod_label_get_labels_by_courses",
        "mod_lti_get_ltis_by_courses",
        "mod_scorm_get_scorms_by_courses",
        "mod_survey_get_surveys_by_courses",
        "mod_h5pactivity_get_h5pactivities_by_courses",
        "mod_chat_get_chats_by_courses",
        "mod_data_get_databases_by_courses",
        "mod_glossary_get_glossaries_by_courses",
        "mod_wiki_get_wikis_by_courses",
        "mod_lesson_get_lessons_by_courses",
        "mod_workshop_get_workshops_by_courses",
        "mod_imscp_get_imscps_by_courses",
    }
)

# ---------------------------------------------------------------------------
# DENYLIST — read-SHAPED functions we deliberately refuse.
#
# These pass a naive "_get_ means read" filter (so the allowlist test would NOT
# catch them), but each either issues a credential, mutates server state, or logs
# a view/completion event. They are listed here so a future reviewer sees they were
# considered and rejected on purpose — do NOT promote any of these into the allowlist.
#
#   tool_mobile_get_autologin_key            issues a login key (a credential)
#   tool_mobile_get_tokens_for_qr_login      issues login tokens (credentials)
#   core_calendar_get_calendar_export_token  issues an iCal export token (credential)
#   mod_lti_get_tool_launch_data             mints a signed LTI launch (acts as the user)
#   mod_bigbluebuttonbn_get_join_url         creates/joins a live BBB session
#   core_files_get_unused_draft_itemid       allocates a server-side draft area (a write)
#   mod_wiki_get_page_for_editing            LOCKS a wiki page for editing (a write)
#   *_view_*  (e.g. mod_forum_view_forum_discussion)  logs a view → can trip completion
# ---------------------------------------------------------------------------
READ_DENYLIST_REVIEWED: frozenset[str] = frozenset(
    {
        "tool_mobile_get_autologin_key",
        "tool_mobile_get_tokens_for_qr_login",
        "core_calendar_get_calendar_export_token",
        "mod_lti_get_tool_launch_data",
        "mod_bigbluebuttonbn_get_join_url",
        "core_files_get_unused_draft_itemid",
        "mod_wiki_get_page_for_editing",
    }
)
