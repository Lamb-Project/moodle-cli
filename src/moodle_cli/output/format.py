"""Small formatting helpers shared by CLI commands."""

from __future__ import annotations

import datetime


def fmt_ts(epoch: int | None) -> str:
    """Render a Unix timestamp as 'YYYY-MM-DD HH:MM', or '-' when empty/zero.

    Moodle returns 0 for "never" (e.g. a user who has never accessed a course),
    so 0 maps to '-' rather than 1970.
    """
    if not epoch:
        return "-"
    try:
        return datetime.datetime.fromtimestamp(int(epoch)).strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError, OverflowError):
        return str(epoch)


def ago(epoch: int | None) -> str:
    """Human 'time since' for a Unix timestamp ('3d', '5h', '12m', 'now', '-')."""
    if not epoch:
        return "-"
    try:
        delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(int(epoch))
    except (ValueError, OSError, OverflowError):
        return str(epoch)
    secs = int(delta.total_seconds())
    if secs < 0:
        return "future"
    if secs < 60:
        return "now"
    if secs < 3600:
        return f"{secs // 60}m"
    if secs < 86400:
        return f"{secs // 3600}h"
    return f"{secs // 86400}d"
