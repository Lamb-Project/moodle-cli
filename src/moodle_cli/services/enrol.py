"""Enrolment service."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from moodle_cli.services.base import BaseService


class EnrolledCourse(BaseModel):
    id: int
    shortname: str
    fullname: str
    enrolledusercount: int = 0
    visible: int = 1
    # Engagement / recency signals returned by core_enrol_get_users_courses.
    # Moodle sends null (not 0) for "never accessed", so these must be nullable.
    lastaccess: int | None = None
    progress: float | None = None
    completed: bool | None = None


class EnrolledUser(BaseModel):
    id: int
    username: str = ""
    fullname: str = ""
    firstname: str = ""
    lastname: str = ""
    email: str = ""
    roles: list[dict[str, Any]] = []
    # Activity signals returned by core_enrol_get_enrolled_users — previously
    # dropped by this model, which hid every engagement stat from the CLI.
    # Nullable: Moodle sends null for a user who has never accessed the course.
    lastaccess: int | None = None
    lastcourseaccess: int | None = None
    groups: list[dict[str, Any]] = []

    @property
    def role_names(self) -> str:
        return ", ".join(r.get("shortname", "") for r in self.roles) or "-"


class EnrolMethod(BaseModel):
    id: int = 0
    courseid: int = 0
    type: str = ""
    name: str = ""
    status: str = ""


class EnrolService(BaseService):
    def get_my_courses(self, userid: int | None = None) -> list[EnrolledCourse]:
        params = {}
        if userid is not None:
            params["userid"] = userid
        data = self.call("core_enrol_get_users_courses", **params)
        return [EnrolledCourse(**c) for c in data]

    def list_enrolled_users(self, course_id: int) -> list[EnrolledUser]:
        data = self.call("core_enrol_get_enrolled_users", courseid=course_id)
        return [EnrolledUser(**u) for u in data]

    def get_enrolment_methods(self, course_id: int) -> list[EnrolMethod]:
        data = self.call("core_enrol_get_course_enrolment_methods", courseid=course_id)
        return [EnrolMethod(**m) for m in data]
