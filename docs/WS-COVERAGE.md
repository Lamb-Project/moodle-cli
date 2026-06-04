# Web-service coverage — what moodle-cli reads, and what it deliberately doesn't

This note records where the **read** surface of `moodle-readonly` stands against
Moodle's core web-service API (per [docs.moodle.org](https://docs.moodle.org/dev/Web_service_API_functions)),
and — more usefully — what is *intentionally* left out, so a future contributor doesn't
re-litigate the same decisions.

The enforced boundary is `src/moodle_cli/client/readonly.py` (`READ_ALLOWLIST` +
`READ_DENYLIST_REVIEWED`). The command surface is `src/moodle_cli/cli/readonly.py`.

## Covered

Identity/site, courses (incl. categories, module, **timeline** by in-progress/past/future),
enrolment (incl. **per-user last access**, methods), groups + groupings, users + per-course
profiles, grades (overview, table, items, report), assignments (list, submissions, grades,
**submission status**), forums (forums, discussions **with reply-count + last poster**, full
**posts** in a thread), quizzes (list, attempts, best grade, **attempt review**), calendar
(all-course **upcoming**, **per-course** events), completion (per-activity + **whole-course**),
**notes**, badges, cohorts, files, messages (conversations, messages, **unread count**),
feedback (list, **analysis**, non-respondents), choice (list, results), and the activity
families via `content list <type>` (resource/page/url/book/folder/label/lti/scorm/survey/
h5p/chat/data/glossary/wiki/lesson/workshop/imscp) plus **content readers** for
workshop (submissions, grades), glossary (entries), database (entries), wiki (pages, page),
lesson (pages).

## Deliberately NOT covered (and why)

**Refused for safety** — read-*shaped* but unsafe; see `READ_DENYLIST_REVIEWED`:
`tool_mobile_get_autologin_key`, `get_tokens_for_qr_login`, `get_calendar_export_token`
(credential/token issuers), `mod_lti_get_tool_launch_data`, `mod_bigbluebuttonbn_get_join_url`
(act-as-user / session creation), `core_files_get_unused_draft_itemid` (allocates a draft —
a write), `mod_wiki_get_page_for_editing` (**locks** the page — a write), any `*_view_*`
(logs a view → can trip completion).

**Skipped as low-value for a teaching/automation CLI** (available, but noise):
- `core_comment_get_comments`, `core_rating_get_item_ratings` — need component+context
  plumbing per call; rarely the question you're asking from a CLI.
- `core_tag_*`, `core_blog_get_entries` — site-wide taxonomy/blog, not course workflow.
- `core_competency_*` (learning plans) — only meaningful on competency-based sites.
- `core_message_get_user_contacts` / `get_blocked_users`, `core_user_get_user_preferences`,
  `core_course_get_recent_courses`, `mod_quiz_get_attempt_summary` — thin value over what's
  already covered (`message unread/conversations`, `enrol my-courses`, `quiz review`).
- `core_calendar_get_calendar_{day,monthly}_view` — heavy view-model payloads; `calendar
  upcoming` / `calendar course` answer the real question.

**Not available on the reference site** (Atenea/UPC token did not expose them, so untestable
here): `core_group_get_group_members` (group membership is instead read via the `groups`
field on `enrol list-users`), `core_notes_get_notes`, `core_grades_get_grades`.

## Adding a read function later

1. Confirm it's a genuine read (no `*_view_*`, no token/lock/launch side effect) — if it's
   read-shaped but unsafe, add it to `READ_DENYLIST_REVIEWED` instead, with a reason.
2. Add it to `READ_ALLOWLIST`, wrap it in a service method + a CLI command, and add the
   command to the `READONLY_COMMANDS` manifest.
3. The boundary tests enforce the invariants (read-shaped, no write verbs, manifest matches).
