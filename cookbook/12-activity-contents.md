# 12 · Reading activity contents

Recipe [04](04-course-activity-stats.md) shows how to **list** the activities in a course
with `content list <type>`. This one goes a level deeper — reading **inside** the activity
types that have their own content: workshops, glossaries, databases, wikis, lessons.

The pattern is always **list the activity to get its id, then read inside it**:

```bash
# 1. which activities of this type are in the course?
moodle-readonly -p default content list <type> <course_id>     # → activity id
# 2. read inside one
moodle-readonly -p default <type> <subcommand> <activity_id>
```

## Workshop (peer assessment)

```bash
moodle-readonly -p default content list workshop <course_id>   # → workshop id
moodle-readonly -p default workshop submissions <workshop_id>  # who submitted what
moodle-readonly -p default workshop grades <workshop_id>       # submission + assessment grades
```

The grades report carries both the **submission grade** and the **assessment grade** (how
well each student peer-reviewed) — the two halves of a workshop mark.

## Glossary

```bash
moodle-readonly -p default content list glossary <course_id>   # → glossary id
moodle-readonly -p default glossary entries <glossary_id>      # concept + definition
```

## Database activity

```bash
moodle-readonly -p default content list data <course_id>       # → database id
moodle-readonly -p default database entries <database_id>      # entries (id, author, approved)
```

## Wiki

```bash
moodle-readonly -p default content list wiki <course_id>       # → wiki id (then find the subwiki)
moodle-readonly -p default wiki pages <subwiki_id>             # list pages in a subwiki
moodle-readonly -p default wiki page <page_id>                 # read one page's text
```

> A wiki has one or more **subwikis** (e.g. per-group); `wiki pages` takes a *subwiki* id.
> The `--json` output of the wiki listing carries the subwiki ids.

## Lesson

```bash
moodle-readonly -p default content list lesson <course_id>     # → lesson id
moodle-readonly -p default lesson pages <lesson_id>            # the lesson's pages
```

## A note on availability

These read the activity *as your account sees it*, so a lesson that has closed, or a
database whose entries need approval, may return a Moodle access message rather than rows —
that's the server enforcing the same rules it would in the browser, not a tool error.

## See also
- [04 · Course activity stats](04-course-activity-stats.md) — listing activities + the
  content inventory.
