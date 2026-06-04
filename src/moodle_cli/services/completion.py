"""Course completion service."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from moodle_cli.services.base import BaseService


class CompletionStatus(BaseModel):
    cmid: int = 0
    modname: str = ""
    instance: int = 0
    state: int = 0
    timecompleted: int = 0
    tracking: int = 0


class CompletionService(BaseService):
    def get_status(self, course_id: int, user_id: int | None = None) -> list[CompletionStatus]:
        params = {"courseid": course_id}
        if user_id is not None:
            params["userid"] = user_id
        data = self.call("core_completion_get_activities_completion_status", **params)
        return [CompletionStatus(**s) for s in data.get("statuses", [])]

    def get_course_status(self, course_id: int, user_id: int) -> dict[str, Any]:
        """Overall course-completion status for a user.

        core_completion_get_course_completion_status — "has this user completed the
        course / how far through the completion criteria are they".
        """
        data = self.call(
            "core_completion_get_course_completion_status",
            courseid=course_id,
            userid=user_id,
        )
        status: dict[str, Any] = data.get("completionstatus", data)
        return status

    def update_status(self, cmid: int, completed: bool) -> None:
        self.call(
            "core_completion_update_activity_completion_status_manually",
            cmid=cmid,
            completed=completed,
        )
