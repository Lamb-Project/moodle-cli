"""Notes commands."""

from __future__ import annotations

import re

import click

from moodle_cli.cli.main import MoodleContext, handle_errors, pass_context
from moodle_cli.output import render_json, render_table, trim
from moodle_cli.services.note import NoteService


@click.group()
def note() -> None:
    """Teacher notes on users."""


@note.command()
@click.argument("course_id", type=int)
@pass_context
@handle_errors
def course(ctx: MoodleContext, course_id: int) -> None:
    """List notes recorded against users in a course."""
    svc = NoteService(ctx.get_client())
    notes = svc.course_notes(course_id)
    if ctx.json_output:
        render_json(notes)
    else:
        rows = [
            {
                "ID": n.get("id"),
                "User": n.get("userid"),
                "Note": trim(
                    re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", n.get("content", ""))).strip(),
                    ctx.trim_messages,
                ),
            }
            for n in notes
        ]
        render_table(rows, title=f"Course notes ({len(rows)})")
