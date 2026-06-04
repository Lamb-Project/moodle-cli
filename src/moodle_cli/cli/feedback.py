"""Feedback (survey) commands."""

from __future__ import annotations

import click

from moodle_cli.cli.main import MoodleContext, handle_errors, pass_context
from moodle_cli.output import console, render_json, render_table
from moodle_cli.services.feedback import FeedbackService


@click.group()
def feedback() -> None:
    """Feedback (survey) activities."""


@feedback.command("list")
@click.argument("course_id", type=int)
@pass_context
@handle_errors
def list_feedbacks(ctx: MoodleContext, course_id: int) -> None:
    """List feedback activities in a course."""
    svc = FeedbackService(ctx.get_client())
    items = svc.list_feedbacks(course_id)
    if ctx.json_output:
        render_json([f.model_dump() for f in items])
    else:
        rows = [{"ID": f.id, "Name": f.name, "Anonymous": f.anonymous} for f in items]
        render_table(rows, title=f"Feedback activities ({len(rows)})")


@feedback.command()
@click.argument("feedback_id", type=int)
@pass_context
@handle_errors
def analysis(ctx: MoodleContext, feedback_id: int) -> None:
    """Aggregated (anonymised) response analysis for a feedback activity."""
    svc = FeedbackService(ctx.get_client())
    data = svc.get_analysis(feedback_id)
    if ctx.json_output:
        render_json(data)
    else:
        console.print(f"Completed responses: {data.get('completedcount', '-')}")
        console.print(f"Total items:         {data.get('itemscount', '-')}")
        for item in data.get("itemsdata", []):
            it = item.get("item", {})
            console.print(f"\n[bold]{it.get('name', '')}[/bold]")
            for line in item.get("data", []):
                console.print(f"  {line}")


@feedback.command("non-respondents")
@click.argument("feedback_id", type=int)
@pass_context
@handle_errors
def non_respondents(ctx: MoodleContext, feedback_id: int) -> None:
    """List enrolled users who have not responded to a feedback activity."""
    svc = FeedbackService(ctx.get_client())
    users = svc.non_respondents(feedback_id)
    if ctx.json_output:
        render_json(users)
    else:
        rows = [{"ID": u.get("userid"), "Name": u.get("fullname", "")} for u in users]
        render_table(rows, title=f"Non-respondents ({len(rows)})")
