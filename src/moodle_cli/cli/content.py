"""Activity-content commands — list activities of a given module type in a course."""

from __future__ import annotations

import click

from moodle_cli.cli.main import MoodleContext, handle_errors, pass_context
from moodle_cli.output import render_json, render_table
from moodle_cli.services.content import CONTENT_TYPES, ContentService


@click.group()
def content() -> None:
    """List activity content by module type (resource, page, url, wiki, …)."""


@content.command("types")
@pass_context
@handle_errors
def types(ctx: MoodleContext) -> None:
    """List the module types `content list` understands."""
    if ctx.json_output:
        render_json(CONTENT_TYPES)
    else:
        render_table([{"Type": t} for t in CONTENT_TYPES], title="Content types")


@content.command("list")
@click.argument("module_type", type=click.Choice(CONTENT_TYPES))
@click.argument("course_id", type=int)
@pass_context
@handle_errors
def list_content(ctx: MoodleContext, module_type: str, course_id: int) -> None:
    """List activities of MODULE_TYPE in a course (e.g. `content list url 106264`)."""
    svc = ContentService(ctx.get_client())
    items = svc.list_activities(module_type, course_id)
    if ctx.json_output:
        render_json(items)
    else:
        rows = [
            {
                "ID": it.get("id"),
                "Name": it.get("name", ""),
                "CM": it.get("coursemodule", ""),
                "Visible": it.get("visible", ""),
            }
            for it in items
        ]
        render_table(rows, title=f"{module_type} ({len(rows)})")
