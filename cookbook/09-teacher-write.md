# 09 · Teacher — write mode

Writing actions a teacher takes, with the full `moodle` binary. **Read
[08 · Write mode overview](08-write-mode-overview.md) first** — these run as you.

> Pattern throughout: **read to get the ids and confirm, then write.**

## Grade a submission

```bash
# 1. Find the assignment + the submission you mean to grade (read-only)
moodle-readonly -p default assign list --course-id 106264
moodle-readonly -p default assign status 635436 --user-id 171768

# 2. Save the grade + feedback (WRITE — recorded as you)
moodle -p default assign grade \
  --assignment-id 635436 --user-id 171768 \
  --grade 8.5 --feedback "Good work — tighten the error handling in section 3."
```

Submissions carry `userid`, not a name, so you can grade `userid + repo` without seeing
the student's identity (blind grading). Resolve a name only if you need to via
`moodle-readonly enrol list-users <course>`.

> **Marking-workflow caveat.** By default `assign grade` saves with an empty workflow
> state, which is correct for assignments with marking workflow **off** (`markingworkflow=0`,
> the common case). If the assignment has marking workflow **on** and you want the grade
> released to the student, add `--workflow-state released`. Do **not** pass a non-empty
> state on a non-workflow assignment — Moodle rejects the whole call with
> `Invalid parameter value detected`.

> **Batch grading pattern** (propose → review → apply): generate a `userid,grade,feedback`
> table from your rubric, eyeball it, then loop:
> ```bash
> while IFS=, read -r uid grade fb; do
>   moodle -p default assign grade --assignment-id 635436 --user-id "$uid" --grade "$grade" --feedback "$fb"
> done < grades.csv
> ```

## Post a forum announcement or reply

```bash
# Announcement to the news forum (find the forum id first)
moodle-readonly -p default forum list 106264          # → news forum id
moodle -p default forum post \
  --forum-id 229498 \
  --subject "Sessió de demà moguda a les 11:00" \
  --message "<p>Hola a tothom, la sessió síncrona de demà passa a les 11:00.</p>"
```

`--message` takes HTML. `forum post` starts a **new discussion**. To reply **within** an
existing thread, use `forum reply` with the parent post's id (from `forum posts <discussion_id>`):

```bash
moodle-readonly -p default forum posts 1445            # → find the post id to reply to
moodle -p default forum reply \
  --post-id 2661 \
  --message "<p>Reply text. Subject defaults to 'Re:' if omitted.</p>"
```

`forum reply` is a write, so it lives only in the full `moodle` binary, never in
`moodle-readonly`. (For drafting the prose, hand it to a writing assistant; for *posting*,
this is the command.)

## Message a student directly

```bash
# user_id then text (positional)
moodle -p default message send 171768 "Hi — could you re-push your repo? The link 404s."
```

## Mark activity completion

```bash
# cmid (course-module id from `course module`/`course contents`) + true|false
moodle -p default completion update 884512 true
```

Useful when an activity's auto-completion missed someone and you want to tick it manually.

## Create a calendar event for the course

```bash
# timestart is a Unix epoch; type=course attaches it to the course
moodle -p default calendar create \
  --name "Lliurament pràctica 3" \
  --timestart "$(date -j -f '%Y-%m-%d %H:%M' '2026-06-12 23:59' +%s)" \
  --duration 0 --type course --course-id 106264 \
  --description "Entrega via el repositori del racó."
```

## Upload a file

```bash
moodle -p default file upload ./handout.pdf --component user --filearea draft
```

## What you can't do from here
- **Reply inside a thread** / edit a post — not a WS command; use the browser.
- **Create activities** (assignments, quizzes) — no WS create for these; browser/import.
- Anything your account lacks the capability for — Moodle refuses it server-side.

## See also
- [02 · Teacher: what to look at](02-teacher-what-to-look-at.md) — the read side.
- [06 · Grades & assignments](06-grades-and-assignments.md).
