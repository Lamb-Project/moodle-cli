"""Offline terminology shared with command help and annotated results."""

from __future__ import annotations

import click

from moodle_cli.cli.main import MoodleContext, pass_context
from moodle_cli.glossary import TERMS, help_for_command, terms_for_command
from moodle_cli.output import render_json


def install_glossary_help(group: click.Group, prefix: str = "") -> None:
    """Attach canonical definitions without changing command execution."""
    for name, command in group.commands.items():
        key = f"{prefix}.{name}" if prefix else name
        if isinstance(command, click.Group):
            install_glossary_help(command, key)
        else:
            notes = help_for_command(key)
            if notes:
                command.epilog = "Field meanings and limitations:\n\n" + notes


@click.command()
@click.argument("term", required=False)
@click.option("--command", "command_key", help="Show terms for a command, e.g. assign.submissions.")
@pass_context
def terms(ctx: MoodleContext, term: str | None, command_key: str | None) -> None:
    """Read the local evidence glossary without connecting to Moodle.

    With no arguments, show every term. This is CLI documentation, not the
    Moodle glossary activity (see `glossary entries`).
    """
    if term and command_key:
        raise click.UsageError("Choose TERM or --command, not both.")
    if term:
        if term not in TERMS:
            raise click.BadParameter(f"Unknown term: {term}", param_hint="TERM")
        selected = {term: TERMS[term]}
    elif command_key:
        selected = terms_for_command(command_key)
        if not selected:
            raise click.BadParameter(f"No glossary terms for command: {command_key}", param_hint="--command")
    else:
        selected = TERMS
    if ctx.json_output:
        render_json(selected)
    else:
        for name, entry in selected.items():
            click.echo(f"{name}: {entry['definition']}")
            if entry.get("limitation"):
                click.echo(f"  Limitation: {entry['limitation']}")
