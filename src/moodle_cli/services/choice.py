"""Choice module service — read-only views of choice activities and their results."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from moodle_cli.services.base import BaseService


class Choice(BaseModel):
    id: int
    course: int = 0
    coursemodule: int = 0
    name: str = ""
    intro: str = ""


class ChoiceService(BaseService):
    def list_choices(self, course_id: int) -> list[Choice]:
        data = self.call(
            "mod_choice_get_choices_by_courses", courseids=[course_id]
        )
        return [Choice(**c) for c in data.get("choices", [])]

    def get_results(self, choice_id: int) -> list[dict[str, Any]]:
        data = self.call("mod_choice_get_choice_results", choiceid=choice_id)
        options: list[dict[str, Any]] = data.get("options", [])
        return options
