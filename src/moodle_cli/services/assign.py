"""Assignment service."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from moodle_cli.services.base import BaseService


class Assignment(BaseModel):
    id: int
    cmid: int = 0
    course: int = 0
    name: str = ""
    duedate: int = 0
    grade: float = 0


class Submission(BaseModel):
    id: int
    userid: int = 0
    status: str = ""
    timemodified: int = 0
    gradingstatus: str = ""


class AssignService(BaseService):
    def list_assignments(self, course_ids: list[int] | None = None) -> list[Assignment]:
        params: dict[str, Any] = {}
        if course_ids:
            params["courseids"] = course_ids
        data = self.call("mod_assign_get_assignments", **params)
        assignments = []
        for course_data in data.get("courses", []):
            for a in course_data.get("assignments", []):
                assignments.append(Assignment(**a))
        return assignments

    def get_submissions(self, assignment_ids: list[int]) -> list[Submission]:
        data = self.call(
            "mod_assign_get_submissions", assignmentids=assignment_ids
        )
        submissions = []
        for a in data.get("assignments", []):
            for s in a.get("submissions", []):
                submissions.append(Submission(**s))
        return submissions

    def get_grades(self, assignment_ids: list[int]) -> list[dict[str, Any]]:
        """Grades already given on assignments (mod_assign_get_grades)."""
        data = self.call("mod_assign_get_grades", assignmentids=assignment_ids)
        grades: list[dict[str, Any]] = []
        for a in data.get("assignments", []):
            for g in a.get("grades", []):
                grades.append({"assignment": a.get("assignmentid"), **g})
        return grades

    def get_submission_status(
        self, assign_id: int, user_id: int | None = None
    ) -> dict[str, Any]:
        """Per-user submission + grading status (mod_assign_get_submission_status)."""
        params: dict[str, Any] = {"assignid": assign_id}
        if user_id is not None:
            params["userid"] = user_id
        status: dict[str, Any] = self.call("mod_assign_get_submission_status", **params)
        return status

    def grade_submission(
        self,
        assignment_id: int,
        user_id: int,
        grade: float,
        feedback: str = "",
        workflow_state: str = "",
    ) -> None:
        # `workflowstate` MUST stay empty unless the assignment has marking
        # workflow enabled (markingworkflow=1). Sending a non-empty state such as
        # "graded" to an assignment with marking workflow OFF makes Moodle reject
        # the whole call with "Invalid parameter value detected" — so the grade
        # never lands. Default to "" (valid for both workflow-on and workflow-off);
        # callers grading a workflow-enabled assignment can pass an explicit state
        # (e.g. "released") via the CLI's --workflow-state.
        self.call(
            "mod_assign_save_grade",
            assignmentid=assignment_id,
            userid=user_id,
            grade=grade,
            attemptnumber=-1,
            addattempt=0,
            workflowstate=workflow_state,
            # `applytoall` is required by mod_assign_save_grade — omitting it is
            # rejected as "Invalid parameter value detected". 0 = grade only this
            # user (correct for a per-user grade; on a team-submission assignment 1
            # would blanket the whole team, which this command must not do).
            applytoall=0,
            plugindata={"assignfeedbackcomments_editor": {"text": feedback, "format": 1}},
        )
