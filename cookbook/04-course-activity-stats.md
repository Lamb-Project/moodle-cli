# 04 · Course activity stats

**Goal:** quantify how alive a course is — who's enrolled, who's actually showing up,
how busy the forums are, and what content is in it.

```bash
C=106264
```

## Enrolment & roles

```bash
moodle-readonly -p default enrol list-users "$C"
```

```bash
# Headcount by role
moodle-readonly -p default --json enrol list-users "$C" \
  | jq -r '[.[].roles[].shortname] | group_by(.) | map({role: .[0], n: length}) | .[] | "\(.n)\t\(.role)"'
# →  25  student
#     1  editingteacher
```

## Engagement — who's actually been here

The enrolled-users list carries each person's **last access to this course**
(`lastcourseaccess`). That's the real engagement signal.

```bash
# How many students have EVER accessed the course
moodle-readonly -p default --json enrol list-users "$C" | jq '
  [ .[] | select(.roles[].shortname=="student") ] as $st
  | { students: ($st|length),
      ever_accessed: ([ $st[] | select((.lastcourseaccess // 0) > 0) ] | length) }'
# →  { "students": 25, "ever_accessed": 21 }

# Active in the last 7 days
now=$(date +%s); wk=$((now - 7*86400))
moodle-readonly -p default --json enrol list-users "$C" \
  | jq --arg wk "$wk" '[ .[] | select((.lastcourseaccess // 0) > ($wk|tonumber)) ] | length'
```

## Forum traffic

```bash
moodle-readonly -p default forum list "$C"
moodle-readonly -p default forum discussions <forum_id>
```

```bash
# Total threads + total replies in a forum
moodle-readonly -p default --json forum discussions <forum_id> | jq '
  { threads: length, replies: ([ .[].numreplies ] | add) }'

# Distinct students who started a thread (participation breadth)
moodle-readonly -p default --json forum discussions <forum_id> \
  | jq '[ .[].userfullname ] | unique | length'
```

## Content inventory — what's in the course

The course's section/module tree:

```bash
moodle-readonly -p default course contents "$C"
```

Or count activities by type using the content lister:

```bash
for t in $(moodle-readonly -p default --json content types | jq -r '.[]'); do
  n=$(moodle-readonly -p default --json content list "$t" "$C" 2>/dev/null | jq 'length // 0')
  [ "${n:-0}" -gt 0 ] && echo "$n  $t"
done
# →  8  lti      (the LAMB assistant embeds)
#     4  page
#     1  resource
```

## Completion (if enabled)

```bash
# A specific student's overall completion
moodle-readonly -p default completion course "$C" --user-id <student_id>
```

## What this CLI can and can't tell you

- ✅ enrolment, roles, **per-user last access**, forum threads + **reply counts + last
  poster**, full thread contents, content inventory, grades, completion, calendar.
- ⚠️ There is no server-side "page views per user" / full activity-log report exposed
  as a Moodle web service, so true click-analytics aren't available to any token-based
  tool — `lastcourseaccess` is the closest engagement proxy.

## See also
- [02 · Teacher triage](02-teacher-what-to-look-at.md).
- [05 · Forums in depth](05-forums.md).
