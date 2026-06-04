"""Enrolment commands."""

from __future__ import annotations

import click

from moodle_cli.cli.main import MoodleContext, handle_errors, pass_context
from moodle_cli.output import ago, fmt_ts, render_json, render_table
from moodle_cli.services.enrol import EnrolService
from moodle_cli.services.user import UserService


@click.group()
def enrol() -> None:
    """Enrolment management."""


@enrol.command("my-courses")
@pass_context
@handle_errors
def my_courses(ctx: MoodleContext) -> None:
    """List courses the current user is enrolled in."""
    client = ctx.get_client()
    user_svc = UserService(client)
    me = user_svc.get_me()
    svc = EnrolService(client)
    courses = svc.get_my_courses(userid=me.id)
    if ctx.json_output:
        render_json([c.model_dump() for c in courses])
    else:
        rows = [
            {
                "ID": c.id,
                "Short Name": c.shortname,
                "Full Name": c.fullname,
                "Last access": ago(c.lastaccess),
            }
            for c in courses
        ]
        render_table(rows, title=f"My Courses ({len(rows)})")


@enrol.command("list-users")
@click.argument("course_id", type=int)
@click.option("--role", default=None, help="Filter by role shortname (e.g. student, editingteacher).")
@pass_context
@handle_errors
def list_users(ctx: MoodleContext, course_id: int, role: str | None) -> None:
    """List enrolled users in a course, with role + last-access (engagement signal)."""
    svc = EnrolService(ctx.get_client())
    users = svc.list_enrolled_users(course_id)
    if role:
        users = [u for u in users if any(r.get("shortname") == role for r in u.roles)]
    if ctx.json_output:
        render_json([u.model_dump() for u in users])
    else:
        rows = [
            {
                "ID": u.id,
                "Full Name": u.fullname,
                "Role": u.role_names,
                "Email": u.email,
                "Last access": fmt_ts(u.lastcourseaccess or u.lastaccess),
                "Ago": ago(u.lastcourseaccess or u.lastaccess),
            }
            for u in users
        ]
        render_table(rows, title=f"Enrolled Users ({len(rows)})")


@enrol.command()
@click.argument("course_id", type=int)
@pass_context
@handle_errors
def methods(ctx: MoodleContext, course_id: int) -> None:
    """List the enrolment methods active in a course."""
    svc = EnrolService(ctx.get_client())
    methods = svc.get_enrolment_methods(course_id)
    if ctx.json_output:
        render_json([m.model_dump() for m in methods])
    else:
        rows = [{"ID": m.id, "Type": m.type, "Name": m.name, "Status": m.status} for m in methods]
        render_table(rows, title=f"Enrolment Methods ({len(rows)})")
