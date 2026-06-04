# 06 · Grades & assignments

**Goal:** read grades (yours or a course's) and inspect assignment submission +
grading status — without any risk of changing a grade.

## Grades

```bash
# Your final grade in every course (one number each)
moodle-readonly -p default grade overview

# Every grade item in one course, for the current user
moodle-readonly -p default grade table <course_id>

# As a teacher, a specific student's grade items
moodle-readonly -p default grade get <course_id> --user-id <student_id>

# Full grade report (all users, all items) for a course
moodle-readonly -p default grade report <course_id>
```

`grade get` / `grade report` use the user grade-items report; `grade table` renders the
grader-style table (item name → grade), stripping Moodle's HTML for you.

## Assignments

```bash
# Assignments in a course
moodle-readonly -p default assign list --course-id <course_id>

# Submissions for an assignment (status + grading status per user)
moodle-readonly -p default assign submissions <assignment_id>

# Grades already awarded
moodle-readonly -p default assign grades <assignment_id>

# One user's submission + grading status for one assignment
moodle-readonly -p default assign status <assignment_id> --user-id <student_id>
```

### Who still needs grading

```bash
moodle-readonly -p default --json assign submissions <assignment_id> | jq -r '
  .[] | select(.status=="submitted" and .gradingstatus=="notgraded") | .userid'
```

### Who hasn't submitted

```bash
# enrolled students  MINUS  users with a submission
C=<course_id>; A=<assignment_id>
comm -23 \
  <(moodle-readonly -p default --json enrol list-users "$C" | jq -r '.[] | select(.roles[].shortname=="student") | .id' | sort -u) \
  <(moodle-readonly -p default --json assign submissions "$A" | jq -r '.[] | select(.status=="submitted") | .userid' | sort -u)
```

## Quizzes

```bash
moodle-readonly -p default quiz list <course_id>
moodle-readonly -p default quiz attempts <quiz_id> --user-id <student_id>
moodle-readonly -p default quiz best-grade <quiz_id> --user-id <student_id>

# Drill into one finished attempt — its questions, marks, and feedback:
moodle-readonly -p default quiz review <attempt_id>          # attempt_id from `quiz attempts`
```

## Note on writes

There is intentionally **no** way to set a grade here — `assign grade`, `grade set`,
etc. do not exist in `moodle-readonly`. Grading is a write; do it in the Moodle UI or
the gated `moodle` binary.

## See also
- [02 · Teacher triage](02-teacher-what-to-look-at.md).
- [03 · Student view](03-student-what-to-look-at.md).
