"""Grade commands."""

from __future__ import annotations

import re

import click

from moodle_cli.cli.main import MoodleContext, handle_errors, pass_context
from moodle_cli.output import console, render_json, render_table
from moodle_cli.services.grade import GradeService


def _strip(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html or "").strip()


@click.group()
def grade() -> None:
    """Grade management."""


@grade.command()
@pass_context
@handle_errors
def overview(ctx: MoodleContext) -> None:
    """Your current final grade in each course you're enrolled in."""
    svc = GradeService(ctx.get_client())
    grades = svc.get_overview()
    if ctx.json_output:
        render_json(grades)
    else:
        rows = [
            {"Course": g.get("courseid"), "Grade": g.get("grade", ""), "Raw": g.get("rawgrade", "")}
            for g in grades
        ]
        render_table(rows, title=f"Grade overview ({len(rows)} courses)")


@grade.command()
@click.argument("course_id", type=int)
@click.option("--user-id", type=int, default=None, help="User ID (defaults to current user)")
@pass_context
@handle_errors
def table(ctx: MoodleContext, course_id: int, user_id: int | None) -> None:
    """Full grader-style grades table for a course."""
    svc = GradeService(ctx.get_client())
    data = svc.get_grades_table(course_id, user_id)
    if ctx.json_output:
        render_json(data)
    else:
        for ut in data.get("tables", []):
            console.print(f"\n[bold]{ut.get('userfullname', ut.get('userid', '?'))}[/bold]")
            for row in ut.get("tabledata", []):
                if not isinstance(row, dict):
                    continue
                item = row.get("itemname", {})
                name = item.get("content", "") if isinstance(item, dict) else str(item)
                grade = row.get("grade", {})
                gval = grade.get("content", "") if isinstance(grade, dict) else str(grade)
                name, gval = _strip(name), _strip(gval)
                if name:
                    console.print(f"  {name}: {gval}")


@grade.command()
@click.argument("course_id", type=int)
@click.option("--user-id", type=int, default=None, help="Filter by user ID")
@pass_context
@handle_errors
def get(ctx: MoodleContext, course_id: int, user_id: int | None) -> None:
    """Get grade items for a course."""
    svc = GradeService(ctx.get_client())
    items = svc.get_grades(course_id, user_id)
    if ctx.json_output:
        render_json([i.model_dump() for i in items])
    else:
        rows = [{"Item": i.itemname or "", "Grade": i.grade or "", "Max": i.grademax} for i in items]
        render_table(rows, title="Grade Items")


@grade.command()
@click.argument("course_id", type=int)
@click.option("--user-id", type=int, default=None, help="Filter by user ID")
@pass_context
@handle_errors
def report(ctx: MoodleContext, course_id: int, user_id: int | None) -> None:
    """Get full grade report for a course."""
    svc = GradeService(ctx.get_client())
    rpt = svc.get_report(course_id, user_id)
    if ctx.json_output:
        render_json(rpt.model_dump())
    else:
        for ug in rpt.usergrades:
            from moodle_cli.output import console
            console.print(f"\n[bold]User: {ug.get('userfullname', ug.get('userid', '?'))}[/bold]")
            items = ug.get("gradeitems", [])
            rows = [
                {"Item": i.get("itemname", ""), "Grade": i.get("grade", ""), "Max": i.get("grademax", "")}
                for i in items
            ]
            render_table(rows)
