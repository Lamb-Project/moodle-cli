# moodle-cli cookbook

Task-oriented recipes for **moodle-cli** — both binaries:

- **`moodle-readonly`** — the read-only, agent-safe twin. Every command only *reads*;
  it cannot grade, enrol, post, or delete. Enforced structurally (no write code path,
  and the HTTP client refuses any non-read function), so it's safe to hand to an AI agent.
- **`moodle`** — the full binary that can also **write** (grade, post, enrol, create,
  delete). Recipes 09–11 use it. It writes **as the authenticated account**, so gate it
  behind human approval — see [08 · Write mode overview](08-write-mode-overview.md).

> All examples use `--profile default`. Drop it if you have a single profile, or swap
> in your own. Add `--json` to any command to get machine-readable output for piping
> into `jq` / a script.

## Recipes

### Read (`moodle-readonly` — agent-safe)

| # | Recipe | Answers |
|---|--------|---------|
| 01 | [My courses & roles](01-my-courses-and-roles.md) | *Which courses am I in, and as what — teacher or student?* |
| 02 | [Teacher: what should I look at?](02-teacher-what-to-look-at.md) | *Unanswered student threads, ungraded work, upcoming deadlines, who's gone quiet.* |
| 03 | [Student: what should I look at?](03-student-what-to-look-at.md) | *My deadlines, my grades, unread messages, my progress.* |
| 04 | [Course activity stats](04-course-activity-stats.md) | *How active is course X — enrolment, engagement, forum traffic, content.* |
| 05 | [Forums in depth](05-forums.md) | *Read a whole thread; find threads waiting on a reply.* |
| 06 | [Grades & assignments](06-grades-and-assignments.md) | *Grade overview, per-course tables, submission + grading status.* |
| 07 | [Finding things](07-finding-things.md) | *Find a course id by name, look up a user, list categories.* |

### Write (`moodle` — gated; writes as you)

| # | Recipe | Covers |
|---|--------|--------|
| 08 | [Write mode overview](08-write-mode-overview.md) | *The two binaries, why writes happen "as you", the safety habits. **Read before 09–11.*** |
| 09 | [Teacher — write mode](09-teacher-write.md) | *Grade, post announcements, message students, mark completion, calendar, upload.* |
| 10 | [Student — write mode](10-student-write.md) | *Post questions, message, own calendar/completion (and what students can't write).* |
| 11 | [Admin — write mode](11-admin.md) | *Course/user CRUD, enrol via `call`, cohorts, roles, the escape hatch.* |

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

## Read vs write — which binary, for whom

`moodle-readonly` is the binary to grant to automation and agents: it cannot change the
site. The write recipes (09–11) use the full `moodle` binary, which acts **as the
authenticated account** — so it belongs to a human (or a human-approved step), not an
unattended agent. The division of labour the cookbook assumes:

- **Agent / script** → `moodle-readonly`. Reads freely, drafts proposals (a grade, a reply).
- **Human** → `moodle`. Reviews the proposal, runs the write.

That boundary is the whole reason there are two binaries. Recipe
[08](08-write-mode-overview.md) explains the safety model before you touch a write command.
