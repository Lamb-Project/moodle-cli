"""Forum commands."""

from __future__ import annotations

import re

import click

from moodle_cli.cli.main import MoodleContext, handle_errors, pass_context
from moodle_cli.output import console, fmt_ts, render_json, render_table, trim
from moodle_cli.services.forum import ForumService


def _plain(html: str) -> str:
    """Strip HTML to plain text. No length cap — trimming (if any) is explicit,
    via ``output.trim`` + the global ``--trim-messages`` option."""
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", text).strip()


@click.group()
def forum() -> None:
    """Forum management."""


@forum.command("list")
@click.argument("course_id", type=int)
@pass_context
@handle_errors
def list_forums(ctx: MoodleContext, course_id: int) -> None:
    """List forums in a course."""
    svc = ForumService(ctx.get_client())
    forums = svc.list_forums(course_id)
    if ctx.json_output:
        render_json([f.model_dump() for f in forums])
    else:
        rows = [{"ID": f.id, "Name": f.name, "Type": f.type} for f in forums]
        render_table(rows, title=f"Forums ({len(rows)})")


@forum.command()
@click.argument("forum_id", type=int)
@pass_context
@handle_errors
def discussions(ctx: MoodleContext, forum_id: int) -> None:
    """List discussions in a forum (with reply count + who posted last)."""
    svc = ForumService(ctx.get_client())
    discs = svc.get_discussions(forum_id)
    if ctx.json_output:
        render_json([d.model_dump() for d in discs])
    else:
        # Moodle returns `id` = first-post id and `discussion` = discussion id.
        # `forum posts` needs the *discussion* id, so surface that as the chainable ID.
        rows = [
            {
                "Disc ID": d.discussion or d.id,
                "Subject": d.subject or d.name,
                "Started by": d.userfullname,
                "Replies": d.numreplies,
                "Last post": fmt_ts(d.timemodified),
                "Last by": d.usermodifiedfullname or "-",
            }
            for d in discs
        ]
        render_table(rows, title=f"Discussions ({len(rows)})")


@forum.command()
@click.argument("discussion_id", type=int)
@pass_context
@handle_errors
def posts(ctx: MoodleContext, discussion_id: int) -> None:
    """List every post in a discussion (author + time, oldest first)."""
    svc = ForumService(ctx.get_client())
    items = svc.get_posts(discussion_id)
    if ctx.json_output:
        render_json([p.model_dump() for p in items])
    else:
        rows = [
            {
                "ID": p.id,
                "When": fmt_ts(p.timecreated),
                "Author": p.author_name,
                "Subject": p.subject,
                "Message": trim(_plain(p.message), ctx.trim_messages),
            }
            for p in items
        ]
        render_table(rows, title=f"Posts ({len(rows)})")


@forum.command()
@click.option("--forum-id", required=True, type=int)
@click.option("--subject", required=True)
@click.option("--message", required=True)
@pass_context
@handle_errors
def post(ctx: MoodleContext, forum_id: int, subject: str, message: str) -> None:
    """Post a new discussion to a forum."""
    svc = ForumService(ctx.get_client())
    disc_id = svc.add_discussion(forum_id, subject, message)
    console.print(f"[green]Created discussion {disc_id} in forum {forum_id}[/green]")


@forum.command()
@click.option(
    "--post-id",
    required=True,
    type=int,
    help="The post to reply to — get its id from `forum posts <discussion_id>`.",
)
@click.option("--subject", default="Re:", help="Reply subject (defaults to 'Re:').")
@click.option("--message", required=True)
@pass_context
@handle_errors
def reply(ctx: MoodleContext, post_id: int, subject: str, message: str) -> None:
    """Reply to a post within an existing discussion thread."""
    svc = ForumService(ctx.get_client())
    new_id = svc.reply_to_post(post_id, subject, message)
    console.print(f"[green]Posted reply {new_id} to post {post_id}[/green]")
