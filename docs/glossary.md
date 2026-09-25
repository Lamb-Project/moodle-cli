# Moodle CLI evidence glossary

Generated from `moodle_cli.glossary`; edit the canonical definitions, not this file.

Scope: the standard API command families exposed by this CLI, not every Moodle feature.
Definitions are deterministic metadata, not evidence that a field is present or an API is available.
Notes apply to the returned account, activity and query context. Raw JSON remains unchanged unless annotation is requested.

The `date_window` and `snapshot` entries are reusable vocabulary for consumers; they do not add date filters or snapshot storage to this CLI.

Validation references: CLI service models; Moodle standard `enrol/externallib.php`, `mod/assign/externallib.php`,
`mod/forum/externallib.php`, `mod/quiz/externallib.php`, and `lib/completionlib.php`.
Moodle versions, permissions and module configuration can change optional fields and visibility.

## Usage

- `moodle terms` lists the full glossary offline; `moodle terms submission_modified` selects a term.
- `moodle terms --command assign.submissions` selects the applicable notes.
- `moodle assign submissions --help` includes the same evidence guidance.
- `moodle --annotated assign submissions 42` returns a `{data, field_notes}` JSON envelope.
- Existing `--json` output is unchanged. `moodle-readonly` supports the same glossary surfaces.
- The Moodle glossary activity remains available as `moodle glossary entries`; it is unrelated to this terminology command.

## response_scope

Results describe records returned for this account, query and retrieval time.

Limit: Permissions, visibility, filters and pagination can restrict coverage. An empty result is not proof of no activity.

Fields/context: `data`, `warnings`.

## missing_value

Absent, null, empty and zero values have field-specific meanings; some CLI models supply defaults for absent fields.

Limit: Do not turn an unavailable or defaulted value into a measured zero, a failure or proof of never participating.

Fields/context: `null`, `0`.

## timestamp

Moodle epoch timestamps are seconds since the Unix epoch; display dates in an explicitly stated timezone.

Limit: A zero or missing timestamp is not automatically an event in 1970. Interpret its documented field sentinel first.

Fields/context: `timecreated`, `timemodified`, `timestart`, `timefinish`.

## date_window

For a consumer using [since, until), since is inclusive and until is exclusive.

Limit: This notation does not claim every Moodle API uses it. To include a calendar day, use the next local midnight as the exclusive end.

Fields/context: `since`, `until`, `timezone`.

## snapshot

A snapshot records evidence observed at its collection time; a delta compares two such observations.

Limit: A first snapshot has no previous baseline. This does not mean Moodle has no historical timestamps or posts.

Fields/context: `as_of`, `collected_at`, `delta`.

## course

A course ID identifies a course on this Moodle site; a course listing is a visibility or enrolment view of that site.

Limit: Listed courses do not establish a teacher role. Names and numeric IDs are not globally unique across sites.

Fields/context: `id`, `courseid`, `fullname`, `shortname`.

## role

Roles are context-scoped assignments; one person may hold multiple roles, including locally defined roles.

Limit: A role label is not a complete effective-capability check. Missing roles do not imply student; do not infer role from course access.

Fields/context: `roles`, `shortname`, `roleid`, `contextid`.

## enrolment

Enrolment links users to courses; enrolledusercount counts enrolled users, not specifically students.

Limit: Teachers and other roles may be included. Enrolment is not evidence of attendance, access or completion.

Fields/context: `enrolledusercount`, `userid`, `courseid`.

## enrolment_method

An enrolment method describes a course enrolment mechanism and its returned status.

Limit: A listed method does not establish that this user is enrolled through it or can self-enrol.

Fields/context: `type`, `status`, `courseid`.

## my_course_lastaccess

In enrol.my-courses, lastaccess is the selected user's most recent recorded access to that course.

Limit: Null may reflect no recorded access or unavailable visibility. One last-access value cannot reconstruct visits or frequency.

Fields/context: `lastaccess`.

## roster_lastaccess

In enrol.list-users, lastaccess refers to the site; lastcourseaccess refers to the queried course. Moodle documents zero as never for these API fields.

Limit: Do not substitute site access for course access. Missing or null is not a measured zero; neither field supplies an access history.

Fields/context: `lastaccess`, `lastcourseaccess`.

## progress

Course progress and completion reflect Moodle's configured completion tracking.

Limit: Unavailable progress is not zero. Progress is not a grade, time spent, or measured learning gain.

Fields/context: `progress`, `completed`.

## module_identity

cmid or coursemodule identifies the course-module link; an activity instance ID identifies a record in its module type.

Limit: These IDs are not interchangeable. Match the requested ID kind before calling an activity API.

Fields/context: `cmid`, `coursemodule`, `instance`, `modname`, `id`.

## resource_listing

Activity and resource listings describe available course content and configuration.

Limit: Listing a resource or file does not show which students opened it, how often, or for how long.

Fields/context: `modules`, `contents`, `url`, `modname`.

## assignment_due

duedate is a due-date value for the assignment in the returned context; zero normally means no due date set.

Limit: Do not declare a learner late without checking applicable extensions, user/group overrides and submission evidence. Due date is not cut-off date.

Fields/context: `duedate`, `cutoffdate`, `extensionduedate`, `allowsubmissionsfromdate`.

## assignment_status

Submission status new is an initial record, draft is not finally submitted, submitted marks submission, and reopened denotes another attempt being opened.

Limit: Record existence is not a submitted exercise. Moodle can create an empty new record while preparing a user's status or grade, so its creation or modification time is not learner activity. Current status is not an event history; group submissions and attempts require their own scope.

Fields/context: `status`, `userid`, `attemptnumber`, `groupid`.

## submission_modified

Submission timemodified is the last modification time of the returned submission record.

Limit: It does not establish the original submission time or a complete history of deliveries and resubmissions.

Fields/context: `timemodified`.

## grading_status

gradingstatus describes grading progress for a submission, distinct from its submission status.

Limit: Graded does not necessarily mean released to the learner; marking-workflow states and visibility matter.

Fields/context: `gradingstatus`, `workflowstate`, `grade`.

## per_user_status

Assignment status is a per-user view; when userid is omitted the API uses the authenticated user.

Limit: A teacher's personal submission status is not the course-wide student submission population.

Fields/context: `userid`, `lastattempt`, `gradingsummary`.

## grade

A grade belongs to its item, scale, range and aggregation context; displayed grade strings may be formatted.

Limit: Null, hidden, ungraded or sentinel values are not automatically zero. A numeric zero may be assigned without a submitted artifact: it proves neither delivery nor lateness. Do not compare raw grades across different scales as percentages.

Fields/context: `grade`, `grademin`, `grademax`, `feedback`.

## assignment_grade_configuration

Assignment grade in the assignment listing configures grading: a positive value is a points maximum, a negative value references a scale, and zero means no grade.

Limit: This is not any student's achieved grade.

Fields/context: `grade`.

## forum_identity

For forum.discussions, id is the first/root post ID and discussion is the discussion ID; forum.posts takes the discussion ID.

Limit: Do not pass the root-post ID where a discussion ID is required. Replies take a parent post ID.

Fields/context: `id`, `discussion`, `discussionid`, `parentid`.

## forum_discussion_activity

Discussion created describes creation; timemodified describes discussion modification/activity; numreplies counts replies rather than the root post.

Limit: Modification is not the creation date of every post. numunread is reader-specific, not total participation.

Fields/context: `created`, `timemodified`, `numreplies`, `numunread`, `usermodified`.

## forum_post

Post timecreated is its creation timestamp; parentid identifies the parent, with no parent for a root post.

Limit: Returned posts are accessible surviving content, not proof of all historic posts, views or reads. Counts alone do not measure contribution quality.

Fields/context: `timecreated`, `parentid`, `author`, `discussionid`.

## activity_completion

Activity completion state: 0 incomplete, 1 complete, 2 complete/pass, 3 complete/fail; tracking: 0 none, 1 manual, 2 automatic.

Limit: Other/version-specific states must not be guessed. Completion reflects configured criteria, not necessarily a resource view or mastery.

Fields/context: `state`, `tracking`, `timecompleted`, `cmid`.

## course_completion

Course completion reports satisfaction of the configured course-completion criteria for the selected user.

Limit: It is distinct from one activity's completion and from a passing final grade; criteria and processing determine its meaning.

Fields/context: `completed`, `completions`, `aggregation`.

## quiz_configuration

Quiz timeopen/timeclose describe configured availability, and grade is the configured maximum grade.

Limit: These are not attempt dates or a learner's achieved grade; individual/group overrides may alter availability.

Fields/context: `timeopen`, `timeclose`, `grade`, `coursemodule`.

## quiz_attempt

A quiz attempt has its own ID, attempt number, state, start and finish timestamps.

Limit: An unfinished attempt is not a finished failure. Attempt count is not participant count; a missing grade is not zero.

Fields/context: `id`, `attempt`, `state`, `timestart`, `timefinish`, `grade`.

## quiz_best_grade

Best-grade response supplies the user's returned quiz grade together with hasgrade when provided.

Limit: Respect hasgrade and the quiz scale; do not infer a zero score when no grade is available.

Fields/context: `grade`, `hasgrade`.

## calendar

Calendar timestart is an event start and timeduration is a duration in seconds; eventtype identifies its kind.

Limit: Calendar events are not activity logs. Empty calendar results do not prove no submissions, forum posts or course activity.

Fields/context: `timestart`, `timeduration`, `eventtype`, `courseid`.

## group

Groups contain course participants; groupings collect groups for course activity configuration.

Limit: A grouping is not a user roster. Group membership does not establish submission, activity or a teacher role.

Fields/context: `id`, `courseid`, `groups`, `groupingid`.

## cohort

A cohort is a site/category-level collection of users, distinct from a course group.

Limit: Cohort membership alone does not establish course enrolment or participation.

Fields/context: `id`, `contextid`, `idnumber`.

## choice_result

Choice results describe options and responses made visible by the activity's settings and permissions.

Limit: Options are not respondents; multiple selections and hidden responses can prevent interpreting option totals as unique students.

Fields/context: `options`, `userresponses`, `users`, `countanswers`.

## feedback

Feedback analysis summarizes visible survey responses; anonymous indicates the activity's anonymity setting.

Limit: Do not deanonymize responses or infer named respondents from aggregates. Non-response is not proof of inactivity elsewhere.

Fields/context: `anonymous`, `itemsdata`, `completedcount`, `users`.

## badge

A returned badge is an award with an issuance date and issuer, optionally associated with a course.

Limit: Issuance date is not necessarily the date of the underlying learning activity; a badge is not an access history.

Fields/context: `dateissued`, `issuername`, `courseid`.

## message

Messages and unread counts belong to the requested user/conversation and its visibility and read state.

Limit: Unread is not evidence that a learner ignored course content; messaging is distinct from forum participation.

Fields/context: `useridfrom`, `useridto`, `timecreated`, `read`, `unreadcount`.

## file

File metadata describes a stored file and its Moodle file-area/context location.

Limit: A file listing is not a download log. Access URLs may require authentication and should not expose tokens.

Fields/context: `filename`, `fileurl`, `contextid`, `component`, `filearea`, `itemid`.

## workshop

Workshop submissions and grades belong to the peer-assessment activity; submission and assessment grades are distinct.

Limit: Do not interpret a workshop grade as an assignment submission grade or an unqualified final course grade.

Fields/context: `grade`, `gradinggrade`, `authorid`, `timecreated`, `timemodified`.

## activity_entry

Glossary/database entries and wiki/lesson pages are activity content records; creation and modification concern those records.

Limit: Retrieving content does not establish views or unique participants. A current page is not a full revision history.

Fields/context: `id`, `timecreated`, `timemodified`, `content`.

## site_function

Advertised web-service functions describe what the connected token's service exposes.

Limit: Advertisement is not a guarantee of permission for every course or user. Missing or denied APIs are not empty datasets.

Fields/context: `functions`, `name`, `userid`.

## user_identity

A user ID identifies an account on this Moodle site; returned profiles expose only selected permitted fields.

Limit: An account is not necessarily a student. A profile lookup does not establish course role or access history.

Fields/context: `id`, `userid`, `fullname`, `email`.

## note

Course notes are access-controlled annotations with their own author, subject and publication context.

Limit: Notes are not a learner activity log or objective measures of achievement.

Fields/context: `content`, `userid`, `publishstate`.

## Command coverage

Every mapped evidence command also includes response-scope and missing-value cautions.

- `assign.grade`: grade, grading_status
- `assign.grades`: grade, grading_status
- `assign.list`: module_identity, assignment_due, assignment_grade_configuration
- `assign.status`: per_user_status, assignment_status, submission_modified, assignment_due, grading_status
- `assign.submissions`: assignment_status, submission_modified, grading_status, timestamp
- `auth.profiles`: offline command; no evidence notes
- `auth.status`: offline command; no evidence notes
- `badge.user`: badge, timestamp
- `calendar.course`: calendar, timestamp
- `calendar.create`: calendar, timestamp
- `calendar.events`: calendar, timestamp
- `calendar.upcoming`: calendar, timestamp
- `choice.list`: module_identity
- `choice.results`: choice_result
- `cohort.add-members`: cohort
- `cohort.create`: cohort
- `cohort.list`: cohort
- `cohort.remove-members`: cohort
- `completion.course`: course_completion
- `completion.status`: module_identity, activity_completion
- `completion.update`: activity_completion
- `content.list`: module_identity, resource_listing
- `content.types`: offline command; no evidence notes
- `course.categories`: course
- `course.contents`: module_identity, resource_listing
- `course.get`: course
- `course.list`: course
- `course.module`: module_identity, resource_listing
- `course.search`: course
- `course.timeline`: course, progress
- `database.entries`: activity_entry
- `enrol.list-users`: enrolment, role, roster_lastaccess, group
- `enrol.methods`: enrolment_method
- `enrol.my-courses`: course, enrolment, my_course_lastaccess, progress
- `feedback.analysis`: feedback
- `feedback.list`: module_identity, feedback
- `feedback.non-respondents`: feedback
- `file.list`: file
- `file.upload`: file
- `forum.discussions`: forum_identity, forum_discussion_activity, timestamp
- `forum.list`: module_identity, response_scope
- `forum.post`: forum_identity
- `forum.posts`: forum_post, timestamp
- `forum.reply`: forum_identity
- `glossary.entries`: activity_entry
- `grade.get`: grade
- `grade.overview`: grade
- `grade.report`: grade
- `grade.table`: grade
- `group.groupings`: group
- `group.list`: group
- `group.user-groups`: group
- `lesson.pages`: activity_entry
- `message.conversations`: message
- `message.list`: message
- `message.send`: message
- `message.unread`: message
- `note.course`: note
- `quiz.attempts`: quiz_attempt, timestamp
- `quiz.best-grade`: quiz_best_grade
- `quiz.list`: module_identity, quiz_configuration
- `quiz.review`: quiz_attempt, grade
- `role.assign`: role
- `role.unassign`: role
- `site.functions`: site_function
- `site.info`: site_function, user_identity
- `user.get`: user_identity
- `user.list`: user_identity
- `user.me`: user_identity
- `user.profiles`: user_identity
- `wiki.page`: activity_entry
- `wiki.pages`: activity_entry
- `workshop.grades`: workshop, grade
- `workshop.submissions`: workshop
