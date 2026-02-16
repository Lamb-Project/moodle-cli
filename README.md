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

## Commands

| Group        | Commands                                      |
|-------------|-----------------------------------------------|
| `auth`      | login, logout, status, profiles               |
| `site`      | info, functions                                |
| `course`    | list, get, search, contents, create, update, delete |
| `user`      | me, list, get, create, update, delete         |
| `enrol`     | my-courses, list-users                        |
| `grade`     | get, report                                   |
| `assign`    | list, submissions, grade                      |
| `forum`     | list, discussions, post                       |
| `quiz`      | list, attempts                                |
| `calendar`  | events, create                                |
| `message`   | send, list, conversations                     |
| `completion` | status, update                               |
| `file`      | upload, list                                  |
| `cohort`    | list, create, delete, add-members, remove-members |
| `role`      | assign, unassign                              |
| `call`      | (generic escape hatch)                        |

## Global Options

- `--profile / -p` — Profile name to use (default: "default")
- `--json` — Output as JSON
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
