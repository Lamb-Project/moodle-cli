"""Tests for assign service."""

from __future__ import annotations

import respx
from httpx import Response

from moodle_cli.client.http import MoodleHTTPClient
from moodle_cli.services.assign import AssignService
from tests.conftest import BASE_URL, TOKEN


class TestAssignService:
    @respx.mock
    def test_grade_submission_sends_applytoall(self) -> None:
        """mod_assign_save_grade rejects the call without `applytoall` —
        regression test for the "Invalid parameter value detected" bug."""
        route = respx.post(f"{BASE_URL}/webservice/rest/server.php").mock(
            return_value=Response(200, text="null")
        )
        client = MoodleHTTPClient(base_url=BASE_URL, token=TOKEN)
        svc = AssignService(client)

        svc.grade_submission(133, 58352, 10.0, feedback="Nice work.")

        assert route.called
        sent = route.calls.last.request.read().decode()
        assert "applytoall=0" in sent
        assert "assignmentid=133" in sent
        assert "userid=58352" in sent
        assert "grade=10.0" in sent
        assert "workflowstate=graded" in sent
