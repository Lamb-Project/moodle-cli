# 01 · My courses & roles

**Goal:** list the courses you're enrolled in and find out what role you play in each
(teacher? student? observer?).

## Your courses

```bash
moodle-readonly -p default enrol my-courses
```

```
                          My Courses (27)
┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ ID     ┃ Short Name ┃ Full Name               ┃ Last access ┃
┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 106264 │ L101v2     │ LAMB 101-v2             │ now         │
│ 104062 │ …ASMI…     │ ASMI 270162             │ 2d          │
└────────┴────────────┴─────────────────────────┴─────────────┘
```

The **Last access** column is your own recency in each course — handy for spotting
courses you've drifted away from.

### Just the active ones (or past / future)

`my-courses` lists everything. To slice by where a course is in its lifecycle:

```bash
moodle-readonly -p default course timeline --classification inprogress
moodle-readonly -p default course timeline --classification past
moodle-readonly -p default course timeline --classification future
```

Good for "what am I actually teaching/taking *this* term" without the archive noise.

## What role do I play in a course?

`my-courses` doesn't carry your role directly. To get it, look yourself up in the
course's enrolled-users list — the **Role** column is the answer:

```bash
# 1. Find your own user id
moodle-readonly -p default user me            # → "ID: 4242"

# 2. List enrolled users and find your row (or filter to teachers)
moodle-readonly -p default enrol list-users 106264 --role editingteacher
```

```
                       Enrolled Users (1)
┏━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━ … ━┳━━━━━━━━━━━━━━━━━━┳━━━━━┓
┃ ID   ┃ Full Name     ┃ Role           ┃ Email ┃ Last access      ┃ Ago ┃
┡━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━ … ━━╇━━━━━━━━━━━━━━━━━━╇━━━━━┩
│ 4242 │ Your Name     │ editingteacher │ …     │ 2026-06-04 09:30 │ now │
└──────┴───────────────┴────────────────┴── … ──┴──────────────────┴─────┘
```

Common role shortnames: `editingteacher` (teacher who can edit), `teacher`
(non-editing / tutor), `student`, `manager`, `guest`.

## JSON for scripting

```bash
# Map every course to your role in it
me=$(moodle-readonly -p default --json user me | jq .id)
for cid in $(moodle-readonly -p default --json enrol my-courses | jq '.[].id'); do
  role=$(moodle-readonly -p default --json enrol list-users "$cid" \
         | jq -r --arg me "$me" '.[] | select(.id==($me|tonumber)) | .roles[].shortname')
  echo "$cid: ${role:-not-enrolled-visibly}"
done
```

## See also
- [04 · Course activity stats](04-course-activity-stats.md) — once you know a course id.
- [07 · Finding things](07-finding-things.md) — find a course id by name.
