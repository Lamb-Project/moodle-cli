"""Output rendering utilities."""

from moodle_cli.output.console import console, error_console
from moodle_cli.output.format import ago, fmt_ts
from moodle_cli.output.json import render_json
from moodle_cli.output.tables import render_table

__all__ = ["ago", "console", "error_console", "fmt_ts", "render_json", "render_table"]
