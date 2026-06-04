# 11 · Admin — write mode

Site-administration workflows with the full `moodle` binary. **Read
[08 · Write mode overview](08-write-mode-overview.md) first.** These need an admin/manager
token and several are **irreversible** — they prompt for confirmation; don't `--yes` them
blind.

> Golden rule for every destructive op: **read it first.** `course get <id>` before
> `course delete <id>`; `user get <id>` before `user delete <id>`.

## Courses

```bash
# Create — needs a category id (course categories → moodle-readonly course categories)
moodle -p default course create \
  --fullname "LAMB 101 — v3 (Tardor 2026)" --shortname "L101v3" --categoryid 42

# Update
moodle -p default course update 106264 --fullname "LAMB 101-v2 (tancat)" --visible 0

# Delete (prompts; recycle-bin behaviour depends on site config)
moodle -p default course delete 106264
```

## Users

```bash
# Create (will prompt for the password if you omit --password)
moodle -p default user create \
  --username jdoe --firstname Jane --lastname Doe --email jane.doe@example.com

# Update
moodle -p default user update 171768 --email new.address@example.com

# Delete (prompts)
moodle -p default user delete 171768
```

## Enrol a user into a course

There's no dedicated `enrol` *write* command — enrolment goes through the `call` escape
hatch with `enrol_manual_enrol_users`. Role ids are site-defined; on a stock Moodle
`5 = student`, `3 = editingteacher`, `4 = teacher` (non-editing).

```bash
# Enrol user 171768 as a student (roleid 5) into course 106264
moodle -p default call enrol_manual_enrol_users \
  -P 'enrolments[0][roleid]=5' \
  -P 'enrolments[0][userid]=171768' \
  -P 'enrolments[0][courseid]=106264'

# Unenrol
moodle -p default call enrol_manual_unenrol_users \
  -P 'enrolments[0][userid]=171768' \
  -P 'enrolments[0][courseid]=106264'
```

> Verify the result with the read side: `moodle-readonly -p default enrol list-users 106264`.

## Cohorts

```bash
moodle -p default cohort create --name "PDI Tardor 2026" --idnumber pdi-2026t --description "Professorat formació LAMB"
moodle-readonly -p default cohort list                       # → new cohort id
moodle -p default cohort add-members <cohort_id> 171768 171769 171770
moodle -p default cohort remove-members <cohort_id> 171770
moodle -p default cohort delete <cohort_id>                  # prompts
```

Cohorts pair well with cohort-sync enrolment: build the cohort here, attach a cohort-sync
enrolment method to a course in the UI, and membership flows automatically.

## Roles

```bash
# Assign / unassign a role to a user IN A CONTEXT.
moodle -p default role assign   --role-id 3 --user-id 171768 --context-id <ctxid>
moodle -p default role unassign --role-id 3 --user-id 171768 --context-id <ctxid>
```

The tricky parameter is **`context-id`** (not a course id): system context is `1`; a
course/module context id you read from `moodle-readonly course module <cmid>` (the `cm`
carries context) or `core_course_get_contents`. For most "make this person a teacher in
this course" needs, prefer the **enrol** route above (it assigns the role as part of
enrolment) over raw `role assign`.

## Bulk / anything-else: the `call` escape hatch

`moodle call <wsfunction> -P key=value` reaches any web-service function with no dedicated
command. Bracket-array params work; quote them so the shell doesn't glob.

```bash
# Full enrolled-users with extra fields
moodle -p default --json call core_enrol_get_enrolled_users \
  -P courseid=106264 \
  -P 'options[0][name]=userfields' -P 'options[0][value]=id,fullname,email,lastcourseaccess'

# Anything the API supports — see `moodle-readonly site functions` for the menu.
```

`call` is unguarded (it's why `moodle-readonly` removes it). Treat it like `sudo`: know
exactly what the wsfunction does before you run it.

## Confirm, then move on
After any write, read it back: `enrol list-users`, `cohort list`, `course get`,
`user get`. The read recipes are your verification layer.

## See also
- [07 · Finding things](07-finding-things.md) — resolving the ids these commands need.
- [08 · Write mode overview](08-write-mode-overview.md) — the safety model.
