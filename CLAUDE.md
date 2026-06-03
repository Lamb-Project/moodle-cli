# CLAUDE.md — moodle-cli

## Project Overview

Python CLI for Moodle Web Services REST API. Supports admin, teacher, and student operations.

## Tech Stack

- Python 3.11+, managed with uv
- Click (CLI), httpx (HTTP), Pydantic v2 (models), Rich (output), keyring (tokens)
- Tests: pytest + respx, Linting: ruff, Types: mypy

## Architecture

```
CLI (Click groups) → Services (typed wrappers) → Client (MoodleHTTPClient.call())
```

- `src/moodle_cli/client/http.py` — core HTTP client, `call(wsfunction, **params)` with bracket-notation param flattening
- `src/moodle_cli/services/*.py` — one per Moodle component, returns Pydantic models
- `src/moodle_cli/cli/*.py` — one Click group per component
- `src/moodle_cli/config/` — TOML profile manager + keyring token store
- `src/moodle_cli/output/` — Rich tables + JSON renderer

## Common Commands

```bash
uv sync                      # Install deps
uv run moodle --help         # Show CLI help
uv run pytest                # Run tests
uv run ruff check src/       # Lint
uv run mypy src/             # Type check
```

## Key Patterns

- All CLI commands use `@pass_context` to get `MoodleContext` (profile, json_output, verbose)
- All CLI commands use `@handle_errors` for friendly error output
- Services extend `BaseService` and access `self.client.call()`
- Token is never stored in config TOML — only in OS keyring
- `call` command is the escape hatch for any WS function

## Adding a New Command Group

1. Create `src/moodle_cli/services/newcomponent.py` extending `BaseService`
2. Create `src/moodle_cli/cli/newcomponent.py` with Click group
3. Register in `src/moodle_cli/cli/main.py` `_register_commands()`
4. Add tests in `tests/test_services/` and `tests/test_cli/`

## Read-only mode — `moodle-readonly` (security boundary)

`moodle-readonly` is a capability-restricted twin entry point: read-only by
construction, intended for AI agents / automation. Two enforcement layers:

- `src/moodle_cli/client/readonly.py` — `READ_ALLOWLIST`, the set of read-only
  `wsfunction`s. **This frozenset is the enforced boundary** (checked in
  `MoodleHTTPClient.call`). Derived by tracing each command to the actual WS
  function it POSTs — never trust the command name.
- `src/moodle_cli/cli/readonly.py` — `READONLY_COMMANDS`, the (group → subcommand)
  filter for the CLI surface, plus the `cli_readonly` entry point.

**When you add a READ command** that should be available to agents: add its
`wsfunction` to `READ_ALLOWLIST` *and* its `(group, subcommand)` to
`READONLY_COMMANDS`. Adding to the allowlist is a security decision — review it.
**Never add a `*_view_*` function** (it logs/triggers completion server-side — a
write). Write commands need no change; they are excluded by default. Tests in
`tests/test_cli/test_readonly.py` enforce the manifest's integrity and that no
write verb sits in the allowlist.
