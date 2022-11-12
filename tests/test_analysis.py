import json
import logging
import os
import uuid
from unittest import mock

from app.utils import rmtree

from .utils import login_user

basedir = os.path.abspath(os.path.dirname(__file__))


def mocked_workflow_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def response(self):
            return self.json_data, self.status_code

        def json(self):
            return self.json_data

    return MockResponse({"status": True, "message": "Analysis started"}, 200)


def test_list_analysis(app, client, analysis):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/analysis/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json.get("analysis")) == 1
    assert resp.json.get("message") == "analysis data sent"

    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{analysis.workflow_id}'
    logging.info(f"Removing workflow directory {workflow_dir}")
    rmtree(workflow_dir)


def test_list_analysis_paging(app, client, two_analysis):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/analysis/?per_page=1", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json.get("analysis")) == 1
    assert resp.json.get("message") == "analysis data sent"

    workflow_dir = (
        f'{app.config["FALCOEYE_ASSETS"]}/workflows/{two_analysis[0].workflow_id}'
    )
    logging.info(f"Removing workflow directory {workflow_dir}")
    rmtree(workflow_dir)


def test_list_analysis_count(client, analysis):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/analysis/count", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "analysis count data sent"
    assert resp.json.get("analysis_count") == 1


@mock.patch("app.api.analysis.service.requests.post", side_effect=mocked_workflow_post)
def test_add_analysis(mock_post, app, client, user, workflow, video):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    data = {
        "name": "FishCounter",
        "workflow_id": str(workflow.id),
        "feeds": {
            "source": {"type": "video", "id": str(video.id)},
            "params": {
                "sample_every": 30,
                "min_score_thresh": 0.30,
                "max_boxes": 30,
            },
        },
    }
    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "analysis added"

    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow.id}'
    logging.info(f"Removing workflow directory {workflow_dir}")
    rmtree(workflow_dir)


@mock.patch("app.api.analysis.service.requests.post", side_effect=mocked_workflow_post)
def test_add_inline_analysis(mock_post, app, client, user, inline_workflow, video):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    data = {
        "name": "TableFinder",
        "workflow_id": str(inline_workflow.id),
        "feeds": {"source": {"type": "video", "id": str(video.id)}, "params": {}},
    }
    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json.get("message") == "analysis done"

    inline_workflow_dir = (
        f'{app.config["FALCOEYE_ASSETS"]}/workflows/{inline_workflow.id}'
    )
    logging.info(f"Removing workflow directory {inline_workflow_dir}")
    rmtree(inline_workflow_dir)


@mock.patch("app.api.analysis.service.requests.post", side_effect=mocked_workflow_post)
def test_edit_analysis(mock_post, app, client, user, workflow, video, streaming_admin):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    data = {
        "name": "FishCounter",
        "workflow_id": str(workflow.id),
        "feeds": {
            "source": {"type": "video", "id": str(video.id)},
            "params": {
                "sample_every": 30,
                "min_score_thresh": 0.30,
                "max_boxes": 30,
            },
        },
    }
    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "analysis added"
    analysis = resp.json.get("analysis")

    resp = login_user(client, streaming_admin["email"], streaming_admin["password"])
    assert "access_token" in resp.json
    admin_access_token = resp.json.get("access_token")

    logging.info("analysis")
    aid = analysis["id"]
    logging.info(f"Analysis id {aid}")
    res = client.put(
        f"/api/analysis/{aid}",
        headers={
            "X-API-KEY": admin_access_token,
            "Content-type": "application/json",
        },
        data=json.dumps({"status": "Completed"}),
    )
    logging.info(res.json)
    assert res.status_code == 200
    assert res.json.get("analysis")["status"] == "Completed"
    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow.id}'
    logging.info(f"Removing workflow directory {workflow_dir}")
    rmtree(workflow_dir)


@mock.patch("app.api.analysis.service.requests.post", side_effect=mocked_workflow_post)
def test_add_analysis_camera(mock_post, app, client, user, workflow, camera):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    data = {
        "name": "FishCounter",
        "workflow_id": str(workflow.id),
        "feeds": {
            "source": {"type": "streaming_source", "id": str(camera.id)},
            "params": {
                "sample_every": 30,
                "min_score_thresh": 0.30,
                "max_boxes": 30,
            },
        },
    }
    resp = client.post(
        "/api/analysis/",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "analysis added"

    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow.id}'
    logging.info(f"Removing workflow directory {workflow_dir}")
    rmtree(workflow_dir)


def test_delete_analysis(app, client, analysis):
    resp = login_user(client)
    assert "access_token" in resp.json
    headers = {"X-API-KEY": resp.json.get("access_token")}
    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{analysis.workflow_id}'
    logging.info(f"Removing workflow directory {workflow_dir}")
    rmtree(workflow_dir)

    resp = client.delete(f"/api/analysis/{analysis.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "analysis deleted"


def test_empty_analysiss(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/analysis/", headers=headers)
    logging.info(resp.json)
    assert resp.json.get("lastPage")
    assert resp.status_code == 200


def test_get_invalid_analysis_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/analysis/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "analysis not found"


def test_delete_invalid_analysis_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/analysis/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "analysis not found"
