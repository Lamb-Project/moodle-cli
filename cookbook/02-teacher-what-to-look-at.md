# 02 · Teacher — what should I look at?

**Goal:** the morning triage. Across the courses you teach, what actually needs you —
student questions waiting on a reply, work to grade, deadlines coming up, students who
have gone quiet.

Set the course once:

```bash
C=106264   # the course you teach
```

## 1. Forum threads waiting on you

List the forums, then the discussions. The discussions table now shows **who posted
last** and **how many replies** — the signal for "a student asked, nobody answered".

```bash
moodle-readonly -p default forum list "$C"
moodle-readonly -p default forum discussions <forum_id>
```

```
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Disc ID ┃ Subject            ┃ Started by   ┃ Replies ┃ Last post    ┃ Last by      ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 647198  │ Equacions (format) │ Luna Alloza  │ 0       │ 2026-06-04   │ Luna Alloza  │  ← ball with you
│ 647185  │ Idiomes i RAG      │ J. Bordonau  │ 0       │ 2026-06-04   │ J. Bordonau  │  ← ball with you
│ 646001  │ Secret key         │ J. Bordonau  │ 3       │ 2026-06-03   │ You          │  ← you answered
└─────────┴────────────────────┴──────────────┴─────────┴──────────────┴──────────────┘
```

**The rule of thumb:** a thread where **Last by ≠ you** and it's a question is one you
probably owe a reply. Read the whole thread before deciding:

```bash
moodle-readonly -p default forum posts 647185
```

> Scripted "ball with me" scan: list discussions as JSON, keep the ones whose last
> poster isn't you.
> ```bash
> moodle-readonly -p default --json forum discussions <forum_id> \
>   | jq -r '.[] | select(.usermodifiedfullname != "Your Name")
>            | "\(.discussion)\t\(.subject)\tlast: \(.usermodifiedfullname)"'
> ```

## 2. Work to grade

```bash
# Assignments in the course, then submission + grading status
moodle-readonly -p default assign list --course-id "$C"
moodle-readonly -p default assign submissions <assignment_id>
```

The submissions table shows `Status` (submitted / new) and `Grading` (graded /
notgraded). Filter for `gradingstatus = notgraded` + `status = submitted` to find the
pile that needs you:

```bash
moodle-readonly -p default --json assign submissions <assignment_id> \
  | jq -r '.[] | select(.status=="submitted" and .gradingstatus=="notgraded") | .userid'
```

## 3. Deadlines coming up

```bash
moodle-readonly -p default calendar upcoming --limit 10        # across ALL your courses
moodle-readonly -p default calendar course "$C"                # just THIS course
```

`upcoming` spans every course soonest-first; `calendar course` narrows to the one you're
triaging — assignment due-dates, quiz closes, scheduled events.

## 4. Who has gone quiet

The enrolled-users list carries each student's **last access to this course**. A `-`
or a large `Ago` is a student who hasn't shown up:

```bash
moodle-readonly -p default enrol list-users "$C" --role student
```

```bash
# Students who have NEVER accessed the course
moodle-readonly -p default --json enrol list-users "$C" \
  | jq -r '.[] | select((.roles[].shortname=="student") and ((.lastcourseaccess // 0)==0)) | .fullname'
```

## 5. Notes you (or a co-teacher) left on students

```bash
moodle-readonly -p default note course "$C"
```

Surfaces the teacher notes recorded against users in the course — easy to lose track of in
the UI.

## 6. Survey / choice pulse (optional)

If you run feedback surveys or choices:

```bash
moodle-readonly -p default feedback list "$C"
moodle-readonly -p default feedback analysis <feedback_id>      # aggregated, anonymous
moodle-readonly -p default feedback non-respondents <feedback_id>
moodle-readonly -p default choice list "$C"
moodle-readonly -p default choice results <choice_id>
```

## See also
- [05 · Forums in depth](05-forums.md) — reading and triaging threads.
- [06 · Grades & assignments](06-grades-and-assignments.md).
