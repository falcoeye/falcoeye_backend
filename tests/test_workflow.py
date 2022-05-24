import datetime
import json
import os
import uuid

from .utils import login_user

basedir = os.path.abspath(os.path.dirname(__file__))


def test_list_workflow(client, workflow):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/workflow/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json.get("workflow")) == 1
    assert resp.json.get("message") == "workflow data sent"


def test_add_workflow(client, user, aimodel):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    data = {
        "name": "FishCounter",
        "creator": str(user.id),
        "aimodel_id": str(aimodel.id),
        "structure_file": f"{basedir}/../../falcoeye_workflow/workflows/kaust_fish_counter_threaded_async.json",
        "usedfor": "detecting stuff",
        "consideration": "be careful",
        "assumption": "barely works",
        "results_description": "stuff",
        "thumbnail_url": "/path/to/thumbnail.jpg",
    }
    resp = client.post(
        "/api/workflow/",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "Workflow has been added."


def test_delete_workflow(client, workflow):
    resp = login_user(client)
    assert "access_token" in resp.json
    headers = {"X-API-KEY": resp.json.get("access_token")}

    resp = client.delete(f"/api/workflow/{workflow.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "workflow deleted"


def test_empty_workflows(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/workflow/", headers=headers)
    assert resp.status_code == 404


def test_get_invalid_workflow_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/workflow/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "Workflow not found!"


def test_delete_invalid_workflow_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/workflow/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "Workflow not found!"
