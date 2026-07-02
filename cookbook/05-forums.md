# 05 · Forums in depth

**Goal:** read a whole discussion, and find the threads that are waiting on a reply.

## The drill-down

```bash
moodle-readonly -p default forum list <course_id>          # forums in the course
moodle-readonly -p default forum discussions <forum_id>    # threads in a forum
moodle-readonly -p default forum posts <discussion_id>     # every post in a thread
```

### A subtlety worth knowing: two different ids

`mod_forum` returns, per discussion, both a first-**post** id and a **discussion** id —
they are different numbers. `forum posts` needs the **discussion** id, so the
`discussions` table prints that one in the **`Disc ID`** column. Use that value:

```bash
moodle-readonly -p default forum discussions 229499
#   Disc ID 647185  "Idiomes i RAG"  …
moodle-readonly -p default forum posts 647185      # ✅ uses the Disc ID
```

## Reading a thread

```bash
moodle-readonly -p default forum posts 647185
```

```
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ ID     ┃ When             ┃ Author          ┃ Subject     ┃ Message         ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 868086 │ 2026-06-04 09:53 │ J. Bordonau     │ Idiomes …   │ Hola, IDIOMES … │
└────────┴──────────────────┴─────────────────┴─────────────┴─────────────────┘
```

Posts come oldest-first, and the table shows the **full message text** — nothing
is cut unless you ask for it. For a compact skim, opt in with the global
`--trim-messages N` flag; a trimmed cell always says how many chars were cut,
so a partial message can never pass for a whole one:

```bash
moodle-readonly -p default --trim-messages 80 forum posts 647185
#   Message: "Hola, IDIOMES i RAG. Volia preguntar si el processador … [… trimmed 412 chars]"
```

> History: table cells used to hard-truncate at 80 chars *silently* — an agent
> reading a post through this command once mistook the first sentence for the
> whole message. That's why the marker is not optional.

For machine consumption, `--json` (always full text, never trimmed):

```bash
moodle-readonly -p default --json forum posts 647185 | jq -r '.[] | "\(.author.fullname): \(.message)"'
```

## Finding threads that await a reply ("ball with me")

A thread needs you when its **last poster isn't you**. The discussions list carries
`usermodifiedfullname` (last poster) and `numreplies`:

```bash
ME="Your Name"
moodle-readonly -p default --json forum discussions <forum_id> | jq -r --arg me "$ME" '
  .[] | select(.usermodifiedfullname != $me)
      | "\(.discussion)\t[\(.numreplies) replies]\tlast: \(.usermodifiedfullname)\t\(.subject)"'
```

Refine it to "student-started AND I never replied" by also checking the starter:

```bash
moodle-readonly -p default --json forum discussions <forum_id> | jq -r --arg me "$ME" '
  .[] | select(.userfullname != $me and .usermodifiedfullname != $me)
      | "\(.discussion)\t\(.subject)"'
```

> This is exactly the "standing forum-debt" detection an assistant agent wants: it
> needs the last-poster + reply-count fields, which `moodle-readonly` now surfaces.

## Announcement vs Q&A forums

Forums have a `type`: `news` (announcements — usually only teachers post) vs `general`
(open Q&A). When triaging student questions, focus on the `general` forums:

```bash
moodle-readonly -p default --json forum list <course_id> | jq -r '.[] | select(.type=="general") | "\(.id)\t\(.name)"'
```

## See also
- [02 · Teacher triage](02-teacher-what-to-look-at.md).
- [04 · Course activity stats](04-course-activity-stats.md).
