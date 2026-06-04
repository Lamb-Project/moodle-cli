"""Feedback (survey) module service — read-only views of feedback activities."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from moodle_cli.services.base import BaseService


class Feedback(BaseModel):
    id: int
    course: int = 0
    coursemodule: int = 0
    name: str = ""
    intro: str = ""
    anonymous: int = 0


class FeedbackService(BaseService):
    def list_feedbacks(self, course_id: int) -> list[Feedback]:
        data = self.call(
            "mod_feedback_get_feedbacks_by_courses", courseids=[course_id]
        )
        return [Feedback(**f) for f in data.get("feedbacks", [])]

    def get_analysis(self, feedback_id: int) -> dict[str, Any]:
        """Aggregated, anonymised analysis of responses (mod_feedback_get_analysis)."""
        analysis: dict[str, Any] = self.call("mod_feedback_get_analysis", feedbackid=feedback_id)
        return analysis

    def non_respondents(self, feedback_id: int) -> list[dict[str, Any]]:
        data = self.call(
            "mod_feedback_get_non_respondents", feedbackid=feedback_id
        )
        users: list[dict[str, Any]] = data.get("users", [])
        return users
