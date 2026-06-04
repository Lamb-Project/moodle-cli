"""Notes service — teacher notes attached to users in a course (read-only)."""

from __future__ import annotations

from typing import Any

from moodle_cli.services.base import BaseService


class NoteService(BaseService):
    def course_notes(self, course_id: int) -> list[dict[str, Any]]:
        """Notes recorded against users in a course (core_notes_get_course_notes)."""
        data = self.call("core_notes_get_course_notes", courseid=course_id)
        notes: list[dict[str, Any]] = data.get("coursenotes", []) if isinstance(data, dict) else []
        return notes
