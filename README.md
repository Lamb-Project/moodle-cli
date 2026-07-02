# moodle-cli

A Python CLI for interacting with Moodle LMS instances via the Web Services REST API.

Copyright (C) 2026 Marc Alier, Juanan Pereira — [LAMB Project](https://github.com/Lamb-Project)
Licensed under the [GNU General Public License v3.0](LICENSE).

## Installation

```bash
uv sync
```

## Quick Start

```bash
# Login to a Moodle instance
moodle auth login --url https://moodle.example.com --username admin

# Check site info
moodle site info

# List courses
moodle course list

# List your enrolled courses
moodle enrol my-courses

# Search courses
moodle course search "math"

# Call any WS function directly
moodle call core_webservice_get_site_info
```

## Authentication with SSO/CAS

Many university Moodle instances use Single Sign-On (SSO/CAS/SAML) for authentication. The `auth login` command uses Moodle's `/login/token.php` endpoint, which requires direct Moodle credentials and **does not work with SSO**.

If your institution uses SSO, you can obtain a token manually:

1. Log in to your Moodle instance normally through your browser (via SSO).
2. Navigate to your **Security keys** page: `https://your-moodle-site.com/user/managetoken.php`
3. Copy an existing token for the **Moodle mobile web service**, or ask your Moodle admin to generate one.

Once you have a token, you can log in with:

```bash
moodle auth login --url https://your-moodle-site.com --username youruser --token YOUR_TOKEN
```

> **Note**: The `--token` flag bypasses the username/password authentication flow and stores the provided token directly.

## QR login (sites that show a QR code instead of a token)

Newer Moodle (4.x) sites often show a **QR code** on the mobile-app / security-keys page instead of a copyable token string. That QR is **not** a token — it encodes a one-time *autologin passport*:

```
moodlemobile://https://your-moodle-site.com?qrlogin=<key>&userid=<id>
```

`moodle auth qr-login` exchanges a **fresh** passport for the real web-service token (via Moodle's `tool_mobile_get_tokens_for_qr_login`) and stores it. This is the **SSO/CAS-friendly** path: it needs no password and no admin, so it works where `auth login --username/--password` cannot.

```bash
# Easiest: point it at a screenshot of the QR (needs the optional `qr` extra, see below)
moodle auth qr-login --image ~/Downloads/qr.png --name mysite

# Or pass the decoded URI yourself (no extra dependency needed) — quote it, it contains &
moodle auth qr-login "moodlemobile://https://your-moodle-site.com?qrlogin=KEY&userid=42" --name mysite

# Or the parts, separately
moodle auth qr-login --url https://your-moodle-site.com --key KEY --userid 42 --name mysite
```

The username is auto-detected from the token; override it with `--username` if needed. Once stored, the profile works with both `moodle` and `moodle-readonly` (shared keyring).

> **Two constraints on the passport.** It is **single-use** and has a **~3-minute TTL** — refresh the QR page right before running the command. A stale key returns `invalidkey`.

**Optional `qr` extra (for `--image`).** Image decoding needs `pyzbar` + `pillow`:

```bash
pip install 'moodle-cli[qr]'
```

`pyzbar` needs the native **zbar** library. On macOS the *system* Python cannot load Homebrew's `libzbar` (SIP strips `DYLD_*`); use a venv/uv Python and point it at the lib:

```bash
brew install zbar
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib moodle auth qr-login --image ~/Downloads/qr.png --name mysite
```

If you'd rather not install anything, decode the QR yourself (any QR reader) and use the `moodlemobile://` URI form above — that path is dependency-free.

## Commands

| Group        | Commands                                      |
|-------------|-----------------------------------------------|
| `auth`      | login, qr-login, logout, status, profiles     |
| `site`      | info, functions                                |
| `course`    | list, get, search, contents, categories, module, timeline, create, update, delete |
| `user`      | me, list, get, profiles, create, update, delete |
| `enrol`     | my-courses, list-users, methods               |
| `grade`     | get, report, overview, table                  |
| `assign`    | list, submissions, grades, status, grade      |
| `forum`     | list, discussions, posts, post                |
| `quiz`      | list, attempts, best-grade, review            |
| `calendar`  | events, upcoming, course, create              |
| `message`   | send, list, conversations, unread             |
| `completion` | status, course, update                       |
| `group`     | list, groupings, user-groups                  |
| `feedback`  | list, analysis, non-respondents               |
| `choice`    | list, results                                 |
| `content`   | types, list (activities by module type)       |
| `note`      | course                                        |
| `workshop`  | submissions, grades                           |
| `glossary`  | entries                                       |
| `database`  | entries                                       |
| `wiki`      | pages, page                                   |
| `lesson`    | pages                                         |
| `badge`     | user                                          |
| `file`      | upload, list                                  |
| `cohort`    | list, create, delete, add-members, remove-members |
| `role`      | assign, unassign                              |
| `call`      | (generic escape hatch)                        |

For the read-only subset of these commands, see [Read-only mode](#read-only-mode-moodle-readonly) below.

## Read-only mode (`moodle-readonly`)

Installing this package gives you a second command, `moodle-readonly`. It does what the name says: it reads from a Moodle site and nothing else. No grading, no enrolment change, no message send, no delete — those commands are not there to run.

It exists for one reason: **handing Moodle access to an AI agent.** An agent that drafts feedback, summarises submissions, or checks who has turned work in needs to read a course. It does not need to change one. The ordinary `moodle` binary does both, so letting an agent run it means trusting it never to call a write — by mistake, or because someone fed it a bad instruction. `moodle-readonly` removes the question: you can give an agent (or any script) free rein over it, because the commands that would do damage do not exist in it to be called. In a permissioned setup, allow `moodle-readonly` outright and keep the full `moodle` behind manual approval.

The guarantee has two parts, and both live in this client — we assume nothing about how the Moodle server is configured.

1. **The write commands are absent.** `moodle-readonly` registers only the read commands. `assign grade`, the `create` / `update` / `delete` of every group, `role assign`, `message send`, and the generic `call` escape hatch are gone — they fail with *no such command* and never appear in `--help`.
2. **The web-service layer refuses writes.** Beneath the commands, the HTTP client holds an allowlist of read-only web-service functions and refuses to call anything outside it. A command that reads as `list` but is wired to a write function would still be stopped here. This is the part that holds even if the command surface ever drifts.

What it does **not** do: it does not make the data harmless. A read-only tool still reads student names, submissions, and grades, and whatever you point it at can pass that on. Read-only governs what gets written back to Moodle, not what gets seen — treat the output with the same care as any other access to student records.

Use it exactly like `moodle`; it shares the same profiles and tokens, so once you have run `moodle auth login`, both commands work:

```bash
moodle-readonly course list
moodle-readonly assign submissions 635436
moodle-readonly grade report 104052
```

### Cookbook

Task-oriented recipes live in [`cookbook/`](cookbook/), split into **read**
(`moodle-readonly`, agent-safe) and **write** (`moodle`, gated) tiers:

- **Read (01–07):** *"which courses am I in and as what role"*, *"as a teacher, what should
  I look at"* (unanswered forum threads, ungraded work, who's gone quiet), *"as a student,
  what's due"*, *"how active is course X"* (enrolment, engagement, forum traffic, content).
- **Write (08–11):** the safety model (writes happen *as you*), then teacher
  (grade, post, message, completion, calendar), student (post, message, own calendar), and
  admin (course/user CRUD, enrol via `call`, cohorts, roles) workflows.

Start at [`cookbook/README.md`](cookbook/README.md).

The read-only surface is built for these workflows: enrolment carries **per-user last
access** (engagement), forum discussions carry **reply counts + last poster** (so you
can spot threads awaiting a reply), and `forum posts` reads a whole thread. The set of
web-service functions the read client may call is reviewed in
[`src/moodle_cli/client/readonly.py`](src/moodle_cli/client/readonly.py), which also
carries a **denylist** of read-*shaped* functions deliberately refused (token/key
issuers, the wiki edit-lock, draft-area allocators, `*_view_*` completion-triggers).

## Global Options

- `--profile / -p` — Profile name to use (default: "default")
- `--json` — Output as JSON (always full text, never trimmed)
- `--trim-messages N` — Trim long text fields (forum posts, messages, summaries, …) in table output to N chars. A trimmed value always ends with `[… trimmed N chars]` so a partial message can never pass for a whole one. **Default: full text — nothing is ever trimmed unless you ask.**
- `--verbose / -v` — Verbose output
- `--version` — Show version

## Architecture

```
CLI Layer (Click) → Service Layer (Pydantic models) → Client Layer (httpx)
```

- **Client**: Single `MoodleHTTPClient.call(wsfunction, **params)` method with bracket-notation parameter flattening
- **Services**: One module per Moodle component, returns typed Pydantic models
- **CLI**: One Click group per component, shared context with `--profile`, `--json`, `--verbose`

## Development

```bash
uv sync
uv run pytest
uv run ruff check src/
uv run mypy src/
```

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

See [LICENSE](LICENSE) for the full text.
