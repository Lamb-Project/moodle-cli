"""JSON output renderer."""

from __future__ import annotations

import json as _json
from typing import Any

import click

from moodle_cli.output.console import console


def render_json(data: Any) -> None:
    """Pretty-print unchanged JSON, or an explicitly requested annotated envelope."""
    ctx = click.get_current_context(silent=True)
    if ctx is not None and getattr(ctx.obj, "annotated", False):
        from moodle_cli.glossary import annotate_result

        parts = []
        current = ctx
        while current.parent is not None:
            parts.append(current.info_name or "")
            current = current.parent
        data = annotate_result(".".join(reversed(parts)), data)
    console.print_json(_json.dumps(data, default=str))
