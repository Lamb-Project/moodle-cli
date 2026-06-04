"""Badge commands."""

from __future__ import annotations

import click

from moodle_cli.cli.main import MoodleContext, handle_errors, pass_context
from moodle_cli.output import fmt_ts, render_json, render_table
from moodle_cli.services.badge import BadgeService
from moodle_cli.services.user import UserService


@click.group()
def badge() -> None:
    """Badges."""


@badge.command("user")
@click.option("--user-id", type=int, default=None, help="User ID (defaults to current user).")
@click.option("--course-id", type=int, default=None, help="Limit to badges from one course.")
@pass_context
@handle_errors
def user_badges(ctx: MoodleContext, user_id: int | None, course_id: int | None) -> None:
    """List a user's awarded badges."""
    client = ctx.get_client()
    if user_id is None:
        user_id = UserService(client).get_me().id
    svc = BadgeService(client)
    badges = svc.user_badges(user_id, course_id)
    if ctx.json_output:
        render_json([b.model_dump() for b in badges])
    else:
        rows = [
            {"ID": b.id, "Name": b.name, "Issued": fmt_ts(b.dateissued), "Issuer": b.issuername}
            for b in badges
        ]
        render_table(rows, title=f"Badges ({len(rows)})")
