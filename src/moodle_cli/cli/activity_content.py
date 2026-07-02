"""Activity-content commands — read the contents of workshop / glossary / database /
wiki / lesson activities (the `content` group lists them; these read inside them)."""

from __future__ import annotations

import re

import click

from moodle_cli.cli.main import MoodleContext, handle_errors, pass_context
from moodle_cli.output import console, render_json, render_table, trim
from moodle_cli.services.activity_content import (
    DatabaseService,
    GlossaryService,
    LessonService,
    WikiService,
    WorkshopService,
)


def _plain(html: str) -> str:
    """Strip HTML to plain text. No length cap — trimming (if any) is explicit,
    via ``output.trim`` + the global ``--trim-messages`` option."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()


# ---- workshop -------------------------------------------------------------
@click.group()
def workshop() -> None:
    """Workshop (peer assessment) activities."""


@workshop.command()
@click.argument("workshop_id", type=int)
@pass_context
@handle_errors
def submissions(ctx: MoodleContext, workshop_id: int) -> None:
    """List submissions to a workshop."""
    items = WorkshopService(ctx.get_client()).submissions(workshop_id)
    if ctx.json_output:
        render_json(items)
    else:
        rows = [
            {"ID": s.get("id"), "Author": s.get("authorid"), "Title": s.get("title", "")}
            for s in items
        ]
        render_table(rows, title=f"Submissions ({len(rows)})")


@workshop.command()
@click.argument("workshop_id", type=int)
@pass_context
@handle_errors
def grades(ctx: MoodleContext, workshop_id: int) -> None:
    """Show the workshop grades report."""
    report = WorkshopService(ctx.get_client()).grades_report(workshop_id)
    if ctx.json_output:
        render_json(report)
    else:
        rows = [
            {
                "User": g.get("userid"),
                "Submission grade": g.get("submissiongrade", "-"),
                "Assessment grade": g.get("gradinggrade", "-"),
            }
            for g in report.get("grades", [])
        ]
        render_table(rows, title=f"Workshop grades ({len(rows)})")


# ---- glossary -------------------------------------------------------------
@click.group()
def glossary() -> None:
    """Glossary activities."""


@glossary.command("entries")
@click.argument("glossary_id", type=int)
@pass_context
@handle_errors
def glossary_entries(ctx: MoodleContext, glossary_id: int) -> None:
    """List glossary entries."""
    items = GlossaryService(ctx.get_client()).entries(glossary_id)
    if ctx.json_output:
        render_json(items)
    else:
        rows = [
            {
                "ID": e.get("id"),
                "Concept": e.get("concept", ""),
                "Definition": trim(_plain(e.get("definition", "")), ctx.trim_messages),
            }
            for e in items
        ]
        render_table(rows, title=f"Glossary entries ({len(rows)})")


# ---- database (data activity) ---------------------------------------------
@click.group()
def database() -> None:
    """Database (data) activities."""


@database.command("entries")
@click.argument("database_id", type=int)
@pass_context
@handle_errors
def database_entries(ctx: MoodleContext, database_id: int) -> None:
    """List entries in a database activity."""
    items = DatabaseService(ctx.get_client()).entries(database_id)
    if ctx.json_output:
        render_json(items)
    else:
        rows = [
            {"ID": e.get("id"), "User": e.get("userid"), "Approved": e.get("approved", "")}
            for e in items
        ]
        render_table(rows, title=f"Database entries ({len(rows)})")


# ---- wiki -----------------------------------------------------------------
@click.group()
def wiki() -> None:
    """Wiki activities."""


@wiki.command("pages")
@click.argument("subwiki_id", type=int)
@pass_context
@handle_errors
def wiki_pages(ctx: MoodleContext, subwiki_id: int) -> None:
    """List pages in a subwiki."""
    items = WikiService(ctx.get_client()).subwiki_pages(subwiki_id)
    if ctx.json_output:
        render_json(items)
    else:
        rows = [
            {"ID": p.get("id"), "Title": p.get("title", ""), "Modified": p.get("timemodified", "")}
            for p in items
        ]
        render_table(rows, title=f"Wiki pages ({len(rows)})")


@wiki.command("page")
@click.argument("page_id", type=int)
@pass_context
@handle_errors
def wiki_page(ctx: MoodleContext, page_id: int) -> None:
    """Read a wiki page's contents."""
    p = WikiService(ctx.get_client()).page_contents(page_id)
    if ctx.json_output:
        render_json(p)
    else:
        console.print(f"[bold]{p.get('title', '')}[/bold]")
        console.print(trim(_plain(p.get("cachedcontent", "")), ctx.trim_messages))


# ---- lesson ---------------------------------------------------------------
@click.group()
def lesson() -> None:
    """Lesson activities."""


@lesson.command("pages")
@click.argument("lesson_id", type=int)
@pass_context
@handle_errors
def lesson_pages(ctx: MoodleContext, lesson_id: int) -> None:
    """List a lesson's pages."""
    items = LessonService(ctx.get_client()).pages(lesson_id)
    if ctx.json_output:
        render_json(items)
    else:
        rows = []
        for entry in items:
            pg = entry.get("page", entry)
            rows.append(
                {
                    "ID": pg.get("id"),
                    "Title": pg.get("title", ""),
                    "Type": pg.get("typestring", pg.get("qtype", "")),
                }
            )
        render_table(rows, title=f"Lesson pages ({len(rows)})")
