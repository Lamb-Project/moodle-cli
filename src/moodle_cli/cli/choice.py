"""Choice commands."""

from __future__ import annotations

import click

from moodle_cli.cli.main import MoodleContext, handle_errors, pass_context
from moodle_cli.output import render_json, render_table
from moodle_cli.services.choice import ChoiceService


@click.group()
def choice() -> None:
    """Choice activities."""


@choice.command("list")
@click.argument("course_id", type=int)
@pass_context
@handle_errors
def list_choices(ctx: MoodleContext, course_id: int) -> None:
    """List choice activities in a course."""
    svc = ChoiceService(ctx.get_client())
    items = svc.list_choices(course_id)
    if ctx.json_output:
        render_json([c.model_dump() for c in items])
    else:
        rows = [{"ID": c.id, "Name": c.name} for c in items]
        render_table(rows, title=f"Choices ({len(rows)})")


@choice.command()
@click.argument("choice_id", type=int)
@pass_context
@handle_errors
def results(ctx: MoodleContext, choice_id: int) -> None:
    """Show the result tally for a choice activity."""
    svc = ChoiceService(ctx.get_client())
    options = svc.get_results(choice_id)
    if ctx.json_output:
        render_json(options)
    else:
        rows = [
            {"Option": o.get("text", ""), "Count": len(o.get("userresponses", []))}
            for o in options
        ]
        render_table(rows, title=f"Results ({len(rows)} options)")
