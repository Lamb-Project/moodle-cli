"""Activity-content service — list activities of a given module type in a course.

One thin wrapper over the family of ``mod_<type>_get_<type>s_by_courses`` read
functions. Rather than a bespoke command per module type, ``content list`` takes a
``--type`` and dispatches to the right web-service function, so the read-only surface
covers every standard activity module without twenty near-identical files.

Every function mapped here is a pure ``_get_..._by_courses`` lister (no view event,
no mutation). The mapping IS the allowlist's content tier — keep them in sync.
"""

from __future__ import annotations

from typing import Any

from moodle_cli.services.base import BaseService

# module type -> (wsfunction, response-list-key)
CONTENT_FUNCTIONS: dict[str, tuple[str, str]] = {
    "resource": ("mod_resource_get_resources_by_courses", "resources"),
    "page": ("mod_page_get_pages_by_courses", "pages"),
    "url": ("mod_url_get_urls_by_courses", "urls"),
    "book": ("mod_book_get_books_by_courses", "books"),
    "folder": ("mod_folder_get_folders_by_courses", "folders"),
    "label": ("mod_label_get_labels_by_courses", "labels"),
    "lti": ("mod_lti_get_ltis_by_courses", "ltis"),
    "scorm": ("mod_scorm_get_scorms_by_courses", "scorms"),
    "survey": ("mod_survey_get_surveys_by_courses", "surveys"),
    "h5p": ("mod_h5pactivity_get_h5pactivities_by_courses", "h5pactivities"),
    "chat": ("mod_chat_get_chats_by_courses", "chats"),
    "data": ("mod_data_get_databases_by_courses", "databases"),
    "glossary": ("mod_glossary_get_glossaries_by_courses", "glossaries"),
    "wiki": ("mod_wiki_get_wikis_by_courses", "wikis"),
    "lesson": ("mod_lesson_get_lessons_by_courses", "lessons"),
    "workshop": ("mod_workshop_get_workshops_by_courses", "workshops"),
    "imscp": ("mod_imscp_get_imscps_by_courses", "imscps"),
}

CONTENT_TYPES = sorted(CONTENT_FUNCTIONS)


class ContentService(BaseService):
    def list_activities(self, module_type: str, course_id: int) -> list[dict[str, Any]]:
        fn, key = CONTENT_FUNCTIONS[module_type]
        data = self.call(fn, courseids=[course_id])
        items: list[dict[str, Any]] = data.get(key, []) if isinstance(data, dict) else data
        return items
