import datetime
import json
import uuid

from .utils import login_user


def test_list_analysis(client, analysis):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/analysis/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json.get("analysis")) == 1
    assert resp.json.get("message") == "analysis data sent"


def test_add_analysis(client, user, workflow):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    data = {
        "name": "FishCounter",
        "creator": str(user.id),
        "workflow_id": str(workflow.id),
        "status": "new",
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
