# 08 · Write mode — the `moodle` binary (read first!)

Recipes 01–07 use **`moodle-readonly`**, which cannot change anything. The recipes that
follow (09 teacher, 10 student, 11 admin) use the **full `moodle`** binary, which **can
write** — grade, post, enrol, create, delete. Read this page before using them.

## Two binaries, one config

| Binary | Can it write? | Hand to an agent? |
|---|---|---|
| `moodle-readonly` | **No** — structurally (recipes 01–07) | **Yes**, freely |
| `moodle` | **Yes** — grade / post / enrol / create / delete | **No** — gate behind manual approval |

Both share the same profiles and tokens, so once `moodle auth login` is done, either
works. Everything below uses `moodle … --profile default`.

## The one rule: writes happen **as you**

A web-service token *is* an identity. When `moodle` posts a forum reply or saves a grade,
Moodle records it as **the account the token belongs to** (here, the teacher). There is no
"acting as a bot" — the action is indistinguishable from you doing it in the browser.

So the discipline for automation/agents is **propose, don't execute**: an assistant drafts
the grade or the message and shows it to you; *you* run the `moodle` command (or approve
it). That's why `moodle-readonly` exists — give the agent that, keep `moodle` for the human.
In a permissioned setup: allow `moodle-readonly` outright, gate `moodle` behind approval.

## Safety habits for write commands

1. **Dry-run by reading first.** Before `assign grade`, run `moodle-readonly assign status`
   to confirm you've got the right user + assignment. Before `course delete`, `course get`.
2. **Destructive commands prompt.** `course delete`, `user delete`, `cohort delete` ask for
   confirmation. Don't script them with `--yes` unless you're certain.
3. **IDs, not names.** Every write takes numeric ids. Resolve them with the read recipes
   ([07 · Finding things](07-finding-things.md)) and double-check before you fire.
4. **There's no undo for most writes.** A saved grade overwrites the old one; a deleted
   course is gone. Moodle has a recycle bin for some deletes, not all.
5. **The `call` escape hatch runs anything.** `moodle call <wsfunction> -P k=v` reaches WS
   functions without a dedicated command (e.g. enrolling a user). Powerful and unguarded —
   treat it like `sudo`.

## What write mode can do (command map)

| Tier | Commands |
|---|---|
| **Teacher** ([09](09-teacher-write.md)) | `assign grade`, `forum post`, `message send`, `completion update`, `calendar create`, `file upload` |
| **Student** ([10](10-student-write.md)) | `forum post`, `message send`, `calendar create`, `completion update` |
| **Admin** ([11](11-admin.md)) | `course create/update/delete`, `user create/update/delete`, `cohort create/delete/add-members/remove-members`, `role assign/unassign`, enrol via `call` |

> Capability still applies on the server: a student token can't grade even though the
> `moodle` binary *offers* `assign grade` — Moodle refuses it. The binary exposes the
> commands; your account's permissions decide what actually goes through.
