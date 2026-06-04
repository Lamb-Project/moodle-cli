# 03 · Student — what should I look at?

**Goal:** as a learner, what's due, how am I doing, and is anything waiting for me.

## 1. What's due soon

```bash
moodle-readonly -p default calendar upcoming --limit 15
```

```
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ When             ┃ Course ┃ Event                     ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2026-06-06 23:59 │ 104062 │ Lliurament pràctica 3     │
│ 2026-06-09 12:00 │ 104135 │ Quiz: tema 5 closes       │
└──────────────────┴────────┴───────────────────────────┘
```

Soonest first, across every course you're enrolled in.

## 2. How am I doing — grades

```bash
# One final number per course
moodle-readonly -p default grade overview

# Every grade item in one course
moodle-readonly -p default grade table <course_id>
```

## 3. My progress through a course

If the course uses activity completion:

```bash
# Per-activity: which boxes are ticked
moodle-readonly -p default completion status <course_id>

# Overall: am I "complete" and which criteria remain
me=$(moodle-readonly -p default --json user me | jq .id)
moodle-readonly -p default completion course <course_id> --user-id "$me"
```

## 4. Anything waiting for me

```bash
# Unread message conversations
moodle-readonly -p default message unread

# The conversations themselves
moodle-readonly -p default message conversations

# New posts in a forum you follow
moodle-readonly -p default forum discussions <forum_id>     # see the "Last post" column
```

## 5. My quiz attempts and best grades

```bash
moodle-readonly -p default quiz list <course_id>
moodle-readonly -p default quiz attempts <quiz_id>
moodle-readonly -p default quiz best-grade <quiz_id>
```

## 6. Badges I've earned

```bash
moodle-readonly -p default badge user
```

## See also
- [01 · My courses & roles](01-my-courses-and-roles.md).
- [06 · Grades & assignments](06-grades-and-assignments.md).
