"""Badges service — a user's awarded badges (read-only)."""

from __future__ import annotations

from pydantic import BaseModel

from moodle_cli.services.base import BaseService


class Badge(BaseModel):
    id: int = 0
    name: str = ""
    description: str = ""
    courseid: int | None = None
    dateissued: int = 0
    issuername: str = ""


class BadgeService(BaseService):
    def user_badges(self, user_id: int, course_id: int | None = None) -> list[Badge]:
        params: dict[str, object] = {"userid": user_id}
        if course_id is not None:
            params["courseid"] = course_id
        data = self.call("core_badges_get_user_badges", **params)
        return [Badge(**b) for b in data.get("badges", [])]
