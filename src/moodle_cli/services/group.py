"""Groups service — course groups, groupings, and a user's group memberships."""

from __future__ import annotations

from pydantic import BaseModel

from moodle_cli.services.base import BaseService


class Group(BaseModel):
    id: int
    courseid: int = 0
    name: str = ""
    description: str = ""
    descriptionformat: int = 1


class Grouping(BaseModel):
    id: int
    courseid: int = 0
    name: str = ""
    description: str = ""


class GroupService(BaseService):
    def list_groups(self, course_id: int) -> list[Group]:
        data = self.call("core_group_get_course_groups", courseid=course_id)
        return [Group(**g) for g in data]

    def list_groupings(self, course_id: int) -> list[Grouping]:
        data = self.call(
            "core_group_get_course_groupings", courseid=course_id
        )
        return [Grouping(**g) for g in data]

    def user_groups(self, course_id: int, user_id: int) -> list[Group]:
        data = self.call(
            "core_group_get_course_user_groups",
            courseid=course_id,
            userid=user_id,
        )
        return [Group(**g) for g in data.get("groups", [])]
