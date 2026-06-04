# 07 · Finding things

**Goal:** translate a human name ("the LAMB course", "that student") into the id the
other commands need.

## Find a course id by name

```bash
# Among the courses you're enrolled in (fast, no site-wide search)
moodle-readonly -p default --json enrol my-courses \
  | jq -r '.[] | select(.fullname|test("LAMB";"i")) | "\(.id)\t\(.shortname)\t\(.fullname)"'

# Site-wide search (needs the search capability on your token)
moodle-readonly -p default course search "LAMB"
```

## Course details & structure

```bash
moodle-readonly -p default course get <course_id>          # name, category, dates, visibility
moodle-readonly -p default course contents <course_id>     # sections + modules
moodle-readonly -p default course categories               # the category tree
moodle-readonly -p default course module <cmid>            # one activity by course-module id
```

## Find a user

```bash
# By email or partial name (wildcard %)
moodle-readonly -p default user list --key email --value "%@estudiantat.upc.edu"
moodle-readonly -p default user get <user_id>

# In the context of one course (role-aware profile)
moodle-readonly -p default user profiles <course_id> <user_id> [<user_id> ...]
```

To find a student's id from a course roster:

```bash
moodle-readonly -p default --json enrol list-users <course_id> \
  | jq -r '.[] | select(.fullname|test("Bordonau";"i")) | "\(.id)\t\(.fullname)\t\(.email)"'
```

## Forums, groups, activities in a course

```bash
moodle-readonly -p default forum list <course_id>
moodle-readonly -p default group list <course_id>
moodle-readonly -p default group groupings <course_id>
moodle-readonly -p default group user-groups <course_id> <user_id>   # which group is this student in?
moodle-readonly -p default content types                   # module types you can list
moodle-readonly -p default content list <type> <course_id> # e.g. content list quiz 106264
moodle-readonly -p default enrol methods <course_id>       # how people get into the course
```

## What can my token even do?

```bash
moodle-readonly -p default site info                       # site + your identity
moodle-readonly -p default site functions                  # every WS function your token has
```

## See also
- [01 · My courses & roles](01-my-courses-and-roles.md).
- [04 · Course activity stats](04-course-activity-stats.md).
