"""Quiz commands."""

from __future__ import annotations

import click

from moodle_cli.cli.main import MoodleContext, handle_errors, pass_context
from moodle_cli.output import console, render_json, render_table, trim
from moodle_cli.services.quiz import QuizService


@click.group()
def quiz() -> None:
    """Quiz management."""


@quiz.command("best-grade")
@click.argument("quiz_id", type=int)
@click.option("--user-id", type=int, default=None, help="User ID (defaults to current user)")
@pass_context
@handle_errors
def best_grade(ctx: MoodleContext, quiz_id: int, user_id: int | None) -> None:
    """Show a user's best grade on a quiz."""
    svc = QuizService(ctx.get_client())
    data = svc.best_grade(quiz_id, user_id)
    if ctx.json_output:
        render_json(data)
    else:
        if data.get("hasgrade"):
            console.print(f"Best grade: {data.get('grade')}")
        else:
            console.print("No grade yet.")


@quiz.command("list")
@click.argument("course_id", type=int)
@pass_context
@handle_errors
def list_quizzes(ctx: MoodleContext, course_id: int) -> None:
    """List quizzes in a course."""
    svc = QuizService(ctx.get_client())
    quizzes = svc.list_quizzes(course_id)
    if ctx.json_output:
        render_json([q.model_dump() for q in quizzes])
    else:
        rows = [{"ID": q.id, "Name": q.name, "Grade": q.grade} for q in quizzes]
        render_table(rows, title=f"Quizzes ({len(rows)})")


@quiz.command()
@click.argument("attempt_id", type=int)
@pass_context
@handle_errors
def review(ctx: MoodleContext, attempt_id: int) -> None:
    """Full review of a finished attempt — questions, marks, feedback."""
    data = QuizService(ctx.get_client()).attempt_review(attempt_id)
    if ctx.json_output:
        render_json(data)
    else:
        import re as _re

        grade = data.get("grade", "-")
        console.print(f"Grade: [bold]{grade}[/bold]")
        for q in data.get("questions", []):
            status = q.get("status", "")
            mark = q.get("mark", "")
            slot = q.get("slot", "")
            html = _re.sub(r"<[^>]+>", " ", q.get("html", "") or "")
            html = trim(_re.sub(r"\s+", " ", html).strip(), ctx.trim_messages)
            console.print(f"  Q{slot} [{status}] mark={mark}: {html}")


@quiz.command()
@click.argument("quiz_id", type=int)
@click.option("--user-id", type=int, default=None, help="Filter by user ID")
@pass_context
@handle_errors
def attempts(ctx: MoodleContext, quiz_id: int, user_id: int | None) -> None:
    """List quiz attempts."""
    svc = QuizService(ctx.get_client())
    atts = svc.get_attempts(quiz_id, user_id)
    if ctx.json_output:
        render_json([a.model_dump() for a in atts])
    else:
        rows = [
            {"ID": a.id, "User": a.userid, "Attempt": a.attempt, "State": a.state, "Grade": a.grade or ""}
            for a in atts
        ]
        render_table(rows, title=f"Attempts ({len(rows)})")
