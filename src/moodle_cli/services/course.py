"""Course service."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from moodle_cli.services.base import BaseService


class Course(BaseModel):
    id: int
    shortname: str
    fullname: str
    categoryid: int = 0
    summary: str = ""
    visible: int = 1
    format: str = "topics"
    startdate: int = 0
    enddate: int = 0


class CourseContent(BaseModel):
    id: int
    name: str
    summary: str = ""
    modules: list[dict[str, Any]] = []


class Category(BaseModel):
    id: int
    name: str = ""
    parent: int = 0
    coursecount: int = 0
    depth: int = 0
    visible: int = 1


class CourseService(BaseService):
    def list_courses(self) -> list[Course]:
        data = self.call("core_course_get_courses")
        return [Course(**c) for c in data]

    def get_categories(self) -> list[Category]:
        data = self.call("core_course_get_categories")
        return [Category(**c) for c in data]

    def get_module(self, cmid: int) -> dict[str, Any]:
        """Course-module metadata by course-module id (core_course_get_course_module)."""
        data = self.call("core_course_get_course_module", cmid=cmid)
        cm: dict[str, Any] = data.get("cm", data)
        return cm

    def get_timeline(self, classification: str = "all") -> list[Course]:
        """Enrolled courses by timeline status — inprogress / past / future / all
        (core_course_get_enrolled_courses_by_timeline_classification)."""
        data = self.call(
            "core_course_get_enrolled_courses_by_timeline_classification",
            classification=classification,
        )
        return [Course(**c) for c in data.get("courses", [])]

    def get_course(self, course_id: int) -> Course:
        data = self.call("core_course_get_courses", options={"ids": [course_id]})
        return Course(**data[0])

    def search_courses(self, query: str) -> list[Course]:
        data = self.call(
            "core_course_search_courses",
            criterianame="search",
            criteriavalue=query,
        )
        return [Course(**c) for c in data.get("courses", [])]

    def get_contents(self, course_id: int) -> list[CourseContent]:
        data = self.call("core_course_get_contents", courseid=course_id)
        return [CourseContent(**s) for s in data]

    def create_course(
        self,
        fullname: str,
        shortname: str,
        categoryid: int,
        **kwargs: Any,
    ) -> Course:
        course_data = {"fullname": fullname, "shortname": shortname, "categoryid": categoryid}
        course_data.update(kwargs)
        data = self.call("core_course_create_courses", courses=[course_data])
        return Course(**data[0])

    def update_course(self, course_id: int, **kwargs: Any) -> None:
        course_data = {"id": course_id, **kwargs}
        self.call("core_course_update_courses", courses=[course_data])

    def delete_courses(self, course_ids: list[int]) -> None:
        self.call("core_course_delete_courses", courseids=course_ids)
