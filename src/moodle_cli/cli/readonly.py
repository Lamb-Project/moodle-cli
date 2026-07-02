"""``moodle-readonly`` — a capability-restricted, read-only twin of the ``moodle`` CLI.

Why this exists
---------------
``moodle-readonly`` can ONLY read. It is the binary you hand to automation — above all,
to AI agents — when you want them to *query* a Moodle instance (list courses, read
submissions, check grades) but must guarantee they cannot *mutate* it (no grading, no
enrolment changes, no message sends, no deletes). The safety is not a promise enforced by
a watching human; it is structural — the binary has no write code path to grant.

Two enforcement layers (both client-side: we do not control the Moodle server, so a
server-scoped read token is not available to us):

1. **Command filter (ergonomic boundary).** Only the (group, subcommand) pairs in
   ``READONLY_COMMANDS`` are registered. Write commands (``assign grade``,
   ``*_create/update/delete``, ``role assign/unassign``, ``message send`` …) and the
   generic ``call`` escape hatch are simply absent — they cannot be invoked or even shown
   in ``--help``. The ``call`` command is *especially* excluded: it builds its own POST and
   bypasses the client chokepoint, so it must never be reachable here.

2. **WS-function allowlist at the HTTP chokepoint (the real boundary).** The client is
   built with ``readonly=True``; ``MoodleHTTPClient.call`` refuses any ``wsfunction`` not in
   ``client.readonly.READ_ALLOWLIST``. This is load-bearing: even if a write command ever
   leaked through layer 1, the client refuses the write at the single point every
   service-based request funnels through.

Relationship to agents: grant ``Bash(moodle-readonly:*)`` to agents (safe by construction)
while keeping the full ``moodle`` binary behind a manual approval gate. See README
"Read-only mode for agents".
"""

from __future__ import annotations

import sys

import click

from moodle_cli import __version__
from moodle_cli.cli.main import MoodleContext

# Which (group -> subcommands) are exposed. Every entry is read-only-verified against the
# service layer. `call` and `role` are absent by design (escape hatch / write-only).
# This is the ergonomic layer; client.readonly.READ_ALLOWLIST is the enforced boundary.
READONLY_COMMANDS: dict[str, set[str]] = {
    "assign": {"list", "submissions", "grades", "status"},
    "auth": {"status", "profiles"},  # local config/keyring reads only
    "badge": {"user"},
    "calendar": {"events", "upcoming", "course"},
    "choice": {"list", "results"},
    "cohort": {"list"},
    "completion": {"status", "course"},
    "content": {"types", "list"},
    "course": {"list", "get", "search", "contents", "categories", "module", "timeline"},
    "database": {"entries"},
    "enrol": {"my-courses", "list-users", "methods"},
    "feedback": {"list", "analysis", "non-respondents"},
    "file": {"list"},
    "forum": {"list", "discussions", "posts"},
    "glossary": {"entries"},
    "grade": {"get", "report", "overview", "table"},
    "group": {"list", "groupings", "user-groups"},
    "lesson": {"pages"},
    "message": {"list", "conversations", "unread"},
    "note": {"course"},
    "quiz": {"list", "attempts", "best-grade", "review"},
    "site": {"info", "functions"},
    "user": {"me", "list", "get", "profiles"},
    "wiki": {"pages", "page"},
    "workshop": {"submissions", "grades"},
}


def _full_groups() -> dict[str, click.Group]:
    """Import the full command groups — the same objects the ``moodle`` CLI registers."""
    from moodle_cli.cli.activity_content import (
        database,
        glossary,
        lesson,
        wiki,
        workshop,
    )
    from moodle_cli.cli.assign import assign
    from moodle_cli.cli.auth import auth
    from moodle_cli.cli.badge import badge
    from moodle_cli.cli.calendar import calendar
    from moodle_cli.cli.choice import choice
    from moodle_cli.cli.cohort import cohort
    from moodle_cli.cli.completion import completion
    from moodle_cli.cli.content import content
    from moodle_cli.cli.course import course
    from moodle_cli.cli.enrol import enrol
    from moodle_cli.cli.feedback import feedback
    from moodle_cli.cli.file import file
    from moodle_cli.cli.forum import forum
    from moodle_cli.cli.grade import grade
    from moodle_cli.cli.group import group
    from moodle_cli.cli.message import message
    from moodle_cli.cli.note import note
    from moodle_cli.cli.quiz import quiz
    from moodle_cli.cli.site import site
    from moodle_cli.cli.user import user

    groups = (
        assign, auth, badge, calendar, choice, cohort, completion, content,
        course, database, enrol, feedback, file, forum, glossary, grade,
        group, lesson, message, note, quiz, site, user, wiki, workshop,
    )
    result: dict[str, click.Group] = {}
    for g in groups:
        assert g.name is not None
        result[g.name] = g
    return result


@click.group()
@click.option("--profile", "-p", default=None, help="Profile name to use.")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON.")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output.")
@click.option(
    "--trim-messages",
    "trim_messages",
    type=click.IntRange(min=1),
    default=None,
    help=(
        "Trim long text fields (forum posts, messages, summaries, …) in table "
        "output to N chars; a trimmed value says how many chars were cut. "
        "Default: full text, never trimmed."
    ),
)
@click.version_option(version=__version__, prog_name="moodle-readonly")
@click.pass_context
def cli_readonly(
    ctx: click.Context,
    profile: str | None,
    json_output: bool,
    verbose: bool,
    trim_messages: int | None,
) -> None:
    """moodle-readonly — read-only Moodle access (safe for agents / automation).

    A capability-restricted twin of `moodle`: query only, never mutate. Write commands
    and the generic `call` escape hatch are not present, and the HTTP client refuses any
    non-read web-service function.

    Copyright (C) 2026 Marc Alier, Juanan Pereira — LAMB Project.
    Licensed under the GNU General Public License v3.0 (GPL-3.0-or-later).
    """
    ctx.ensure_object(dict)
    ctx.obj = MoodleContext(
        profile=profile,
        json_output=json_output,
        verbose=verbose,
        readonly=True,
        trim_messages=trim_messages,
    )


def _register_readonly_commands() -> None:
    """Register a filtered copy of each group, keeping only read-allowlisted subcommands."""
    for gname, group in _full_groups().items():
        allowed = READONLY_COMMANDS.get(gname)
        if not allowed:
            continue
        filtered = click.Group(name=group.name, help=group.help)
        for sub_name, sub_cmd in group.commands.items():
            if sub_name in allowed:
                filtered.add_command(sub_cmd, sub_name)
        # Fail loud at import time if the manifest names a command that no longer exists —
        # silent drift in a security manifest is the failure mode we refuse to ship.
        missing = allowed - set(filtered.commands)
        if missing:
            print(
                f"moodle-readonly: manifest error — group '{gname}' has no command(s): "
                f"{sorted(missing)}",
                file=sys.stderr,
            )
        if filtered.commands:
            cli_readonly.add_command(filtered)


_register_readonly_commands()
