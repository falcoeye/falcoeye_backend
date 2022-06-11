import datetime
import json
import os
import uuid
from unittest import mock

from .utils import login_user

basedir = os.path.abspath(os.path.dirname(__file__))


def mocked_workflow_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def response(self):
            return self.json_data, self.status_code

    return MockResponse({"status": True, "message": "Analysis started"}, 200)


def test_list_analysis(client, analysis):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/analysis/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json.get("analysis")) == 1
    assert resp.json.get("message") == "Analysis data sent"


@mock.patch("app.api.analysis.service.requests.post", side_effect=mocked_workflow_post)
def test_add_analysis(mock_post, client, user, workflow):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    data = {
        "name": "FishCounter",
        "creator": str(user.id),
        "workflow_id": str(workflow.id),
        "status": "new",
        "args": {
            "filename": f"{basedir}/tests/media/lutjanis.mov",
            "sample_every": 30,
            "min_score_thresh": 0.30,
            "max_boxes": 30,
        },
    }
    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "Analysis has been added."


def test_delete_analysis(client, analysis):
    resp = login_user(client)
    assert "access_token" in resp.json
    headers = {"X-API-KEY": resp.json.get("access_token")}

    resp = client.delete(f"/api/analysis/{analysis.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "analysis deleted"


def test_empty_analysiss(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/analysis/", headers=headers)
    assert resp.status_code == 404


def test_get_invalid_analysis_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/analysis/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "Analysis not found!"


def test_delete_invalid_analysis_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/analysis/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "Analysis not found!"