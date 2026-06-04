"""Group commands."""

from __future__ import annotations

import click

from moodle_cli.cli.main import MoodleContext, handle_errors, pass_context
from moodle_cli.output import render_json, render_table
from moodle_cli.services.group import GroupService


@click.group()
def group() -> None:
    """Groups and groupings."""


@group.command("list")
@click.argument("course_id", type=int)
@pass_context
@handle_errors
def list_groups(ctx: MoodleContext, course_id: int) -> None:
    """List groups in a course."""
    svc = GroupService(ctx.get_client())
    groups = svc.list_groups(course_id)
    if ctx.json_output:
        render_json([g.model_dump() for g in groups])
    else:
        rows = [{"ID": g.id, "Name": g.name} for g in groups]
        render_table(rows, title=f"Groups ({len(rows)})")


@group.command()
@click.argument("course_id", type=int)
@pass_context
@handle_errors
def groupings(ctx: MoodleContext, course_id: int) -> None:
    """List groupings in a course."""
    svc = GroupService(ctx.get_client())
    items = svc.list_groupings(course_id)
    if ctx.json_output:
        render_json([g.model_dump() for g in items])
    else:
        rows = [{"ID": g.id, "Name": g.name} for g in items]
        render_table(rows, title=f"Groupings ({len(rows)})")


@group.command("user-groups")
@click.argument("course_id", type=int)
@click.argument("user_id", type=int)
@pass_context
@handle_errors
def user_groups(ctx: MoodleContext, course_id: int, user_id: int) -> None:
    """List the groups a user belongs to in a course."""
    svc = GroupService(ctx.get_client())
    groups = svc.user_groups(course_id, user_id)
    if ctx.json_output:
        render_json([g.model_dump() for g in groups])
    else:
        rows = [{"ID": g.id, "Name": g.name} for g in groups]
        render_table(rows, title=f"Groups for user {user_id} ({len(rows)})")
