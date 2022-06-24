import datetime
import json
import logging
import os
import shutil
import uuid

from .utils import login_user

basedir = os.path.abspath(os.path.dirname(__file__))


def test_list_workflow(app, client, workflow):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/workflow/", headers=headers)
    assert resp.status_code == 200
    logging.info(resp.json.get("workflow"))
    assert len(resp.json.get("workflow")) == 1
    assert resp.json.get("message") == "workflow data sent"
    workflow_id = str(workflow.id)
    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}'
    logging.info(f"Removing workflow directory {workflow_dir}")
    shutil.rmtree(workflow_dir)


def test_add_workflow(client, app, user, aimodel):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    with open(
        f"{basedir}/../../falcoeye_workflow/workflows/kaust_fish_counter_threaded_async.json"
    ) as f:
        structure = json.load(f)
    data = {
        "name": "FishCounter",
        "creator": str(user.id),
        "aimodel_id": str(aimodel.id),
        "structure": structure,
        "usedfor": "detecting stuff",
        "consideration": "be careful",
        "assumption": "barely works",
        "results_description": "stuff",
    }
    resp = client.post(
        "/api/workflow/",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "Workflow has been added."

    workflow_id = resp.json.get("workflow").get("id")
    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}'
    logging.info(f"Removing workflow directory {workflow_dir}")
    shutil.rmtree(workflow_dir)


def test_delete_workflow(app, client, workflow):
    resp = login_user(client)
    assert "access_token" in resp.json
    headers = {"X-API-KEY": resp.json.get("access_token")}
    workflow_id = str(workflow.id)
    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}'
    logging.info(f"Removing workflow directory {workflow_dir}")
    shutil.rmtree(workflow_dir)

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
