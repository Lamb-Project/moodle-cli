"""Activity-content services — read the *contents* of activities the `content`
group can only list (workshop, glossary, database, wiki, lesson).

These complete the "list an activity, then read what's inside it" story. Every
function here is a pure read (`_get_`), no view-event, no mutation.
"""

from __future__ import annotations

from typing import Any

from moodle_cli.services.base import BaseService


class WorkshopService(BaseService):
    def submissions(self, workshop_id: int) -> list[dict[str, Any]]:
        data = self.call("mod_workshop_get_submissions", workshopid=workshop_id)
        subs: list[dict[str, Any]] = data.get("submissions", []) if isinstance(data, dict) else []
        return subs

    def grades_report(self, workshop_id: int) -> dict[str, Any]:
        data = self.call("mod_workshop_get_grades_report", workshopid=workshop_id)
        report: dict[str, Any] = data.get("report", data) if isinstance(data, dict) else {}
        return report


class GlossaryService(BaseService):
    def entries(self, glossary_id: int, letter: str = "ALL") -> list[dict[str, Any]]:
        data = self.call(
            "mod_glossary_get_entries_by_letter", id=glossary_id, letter=letter
        )
        entries: list[dict[str, Any]] = data.get("entries", []) if isinstance(data, dict) else []
        return entries


class DatabaseService(BaseService):
    def entries(self, database_id: int) -> list[dict[str, Any]]:
        data = self.call("mod_data_get_entries", databaseid=database_id)
        entries: list[dict[str, Any]] = data.get("entries", []) if isinstance(data, dict) else []
        return entries


class WikiService(BaseService):
    def subwiki_pages(self, subwiki_id: int) -> list[dict[str, Any]]:
        data = self.call("mod_wiki_get_subwiki_pages", subwikiid=subwiki_id)
        pages: list[dict[str, Any]] = data.get("pages", []) if isinstance(data, dict) else []
        return pages

    def page_contents(self, page_id: int) -> dict[str, Any]:
        data = self.call("mod_wiki_get_page_contents", pageid=page_id)
        page: dict[str, Any] = data.get("page", data) if isinstance(data, dict) else {}
        return page


class LessonService(BaseService):
    def pages(self, lesson_id: int) -> list[dict[str, Any]]:
        data = self.call("mod_lesson_get_pages", lessonid=lesson_id)
        pages: list[dict[str, Any]] = data.get("pages", []) if isinstance(data, dict) else []
        return pages
