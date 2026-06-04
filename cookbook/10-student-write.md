# 10 · Student — write mode

What a learner account can write with the full `moodle` binary. **Read
[08 · Write mode overview](08-write-mode-overview.md) first** — these run as you.

A student token is limited by capability: the `moodle` binary *offers* every write
command, but Moodle refuses the ones a student can't do (grading, enrolling others,
creating courses). What a student can actually write:

## Ask a question in a forum

```bash
# find the open Q&A forum, then post a new discussion
moodle-readonly -p default forum list <course_id>     # pick the 'general' forum
moodle -p default forum post \
  --forum-id <forum_id> \
  --subject "Dubte sobre el RAG amb enllaços" \
  --message "<p>Es pot passar una URL com a font RAG, o només fitxers .txt?</p>"
```

`--message` is HTML. This starts a new thread; replying inside an existing thread isn't a
WS command — do that in the browser.

## Message a teacher or classmate

```bash
moodle -p default message send <user_id> "Hi — could we meet about the TFM this week?"
```

Find the recipient's id from a course roster you share:
`moodle-readonly -p default enrol list-users <course_id>`.

## Put a personal deadline on your calendar

```bash
moodle -p default calendar create \
  --name "Acabar pràctica 2" \
  --timestart "$(date -j -f '%Y-%m-%d %H:%M' '2026-06-10 18:00' +%s)" \
  --type user \
  --description "Recordatori personal"
```

`--type user` is a private event (only you see it).

## Mark an activity complete (if the activity allows manual completion)

```bash
moodle -p default completion update <cmid> true
```

Only works where the teacher set the activity to "students manually mark complete".

## What a student **can't** do over web services
- **Submit an assignment** — there is no `mod_assign_save_submission` exposed as a command,
  and most sites don't enable it for the mobile WS. Submit in the browser.
- **Submit a quiz attempt** — same; quiz-taking is browser-only here.
- Grade, enrol, or change anyone else's data — refused server-side.

So a student's write surface is essentially **communicate** (forum, message) and
**self-organise** (own calendar, own completion). The graded work itself goes through the
Moodle UI.

## See also
- [03 · Student: what to look at](03-student-what-to-look-at.md) — the read side.
