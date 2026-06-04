# moodle-readonly cookbook

Task-oriented recipes for **`moodle-readonly`** — the read-only, agent-safe twin of
`moodle`. Every command here only *reads*: it cannot grade, enrol, post, or delete.
That is enforced structurally (the binary has no write code path and the HTTP client
refuses any non-read web-service function), so these recipes are safe to hand to an
automation or an AI agent verbatim.

> All examples use `--profile default`. Drop it if you have a single profile, or swap
> in your own. Add `--json` to any command to get machine-readable output for piping
> into `jq` / a script.

## Recipes

| # | Recipe | Answers |
|---|--------|---------|
| 01 | [My courses & roles](01-my-courses-and-roles.md) | *Which courses am I in, and as what — teacher or student?* |
| 02 | [Teacher: what should I look at?](02-teacher-what-to-look-at.md) | *Unanswered student threads, ungraded work, upcoming deadlines, who's gone quiet.* |
| 03 | [Student: what should I look at?](03-student-what-to-look-at.md) | *My deadlines, my grades, unread messages, my progress.* |
| 04 | [Course activity stats](04-course-activity-stats.md) | *How active is course X — enrolment, engagement, forum traffic, content.* |
| 05 | [Forums in depth](05-forums.md) | *Read a whole thread; find threads waiting on a reply.* |
| 06 | [Grades & assignments](06-grades-and-assignments.md) | *Grade overview, per-course tables, submission + grading status.* |
| 07 | [Finding things](07-finding-things.md) | *Find a course id by name, look up a user, list categories.* |

## The two-step pattern

Almost every recipe is **find an id, then drill in**. Moodle is id-addressed: you
list to discover the id, then pass it to the next command.

```bash
moodle-readonly -p default enrol my-courses          # → course id
moodle-readonly -p default forum list <course_id>    # → forum id
moodle-readonly -p default forum discussions <forum_id>   # → discussion id
moodle-readonly -p default forum posts <discussion_id>    # → the thread
```

## Reading timestamps

Tables render times as `YYYY-MM-DD HH:MM` and recency as `3d` / `5h` / `now`.
A `-` means "never" (e.g. a student who has never opened the course). With `--json`
you get the raw Unix epoch instead.

## Safety note for agents

`moodle-readonly` is the binary to grant to automation. The write-capable `moodle`
binary is a separate tool kept behind a manual gate. If a recipe seems to want a write
(post a reply, set a grade), that is by design out of scope here — surface the draft to
a human and let them act.
