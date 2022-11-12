import base64
import json
import logging
import os
import uuid

from app.utils import rmtree

from .utils import login_user


def get_base64img(imgfile):
    with open(imgfile, "rb") as image_file:
        data = base64.b64encode(image_file.read())
    return data.decode("utf-8")


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

    rmtree(workflow_dir)


def test_list_workflow_paged(app, client, two_workflow):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/workflow/?per_page=1", headers=headers)
    assert resp.status_code == 200
    logging.info(resp.json.get("workflow"))
    assert len(resp.json.get("workflow")) == 1
    assert resp.json.get("message") == "workflow data sent"
    workflow_id = str(two_workflow[0].id)
    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}'
    logging.info(f"Removing workflow directory {workflow_dir}")

    rmtree(workflow_dir)


def test_list_workflow_count(client, workflow):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/workflow/count", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "workflow count data sent"
    assert resp.json.get("workflow_count") == 1


def test_get_workflow_by_id(app, client, workflow):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/workflow/{workflow.id}", headers=headers)
    assert resp.status_code == 200
    logging.info(resp.json.get("workflow"))


def test_add_workflow_with_img(client, app, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    with open(
        f"{basedir}/../initialization/workflows/kaust_fish_counter_threaded_async_grpc.json"
    ) as f:
        structure = json.load(f)
    data = {
        "name": "FishCounter",
        "creator": str(user.id),
        "structure": structure,
        "usedfor": "detecting stuff",
        "consideration": "be careful",
        "assumption": "barely works",
        "results_description": "stuff",
    }
    base64img = get_base64img(f"{basedir}/media/fish.jpg")
    data["image"] = base64img

    resp = client.post(
        "/api/workflow/",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "workflow added"

    workflow_id = resp.json.get("workflow").get("id")
    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}'
    logging.info(f"Removing workflow directory {workflow_dir}")
    rmtree(workflow_dir)


def test_add_workflow(client, app, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    with open(
        f"{basedir}/../initialization/workflows/kaust_fish_counter_threaded_async_grpc.json"
    ) as f:
        structure = json.load(f)
    data = {
        "name": "FishCounter",
        "creator": str(user.id),
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
    assert resp.json.get("message") == "workflow added"

    workflow_id = resp.json.get("workflow").get("id")
    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}'
    logging.info(f"Removing workflow directory {workflow_dir}")
    rmtree(workflow_dir)


def test_add_inline_workflow(client, app, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    with open(f"{basedir}/../initialization/inline_workflows/table_finder.json") as f:
        structure = json.load(f)
    data = {
        "name": "TableFinder",
        "creator": str(user.id),
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
    assert resp.json.get("message") == "workflow added"

    workflow_id = resp.json.get("workflow").get("id")
    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}'
    logging.info(f"Removing workflow directory {workflow_dir}")
    rmtree(workflow_dir)


def test_workflow_params(client, app, workflow):
    resp = login_user(client)
    assert "access_token" in resp.json
    headers = {"X-API-KEY": resp.json.get("access_token")}
    workflow_id = str(workflow.id)
    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}'
    resp = client.get(
        f"/api/workflow/{workflow_id}/params",
        content_type="application/json",
        headers=headers,
    )
    logging.info(resp.json)
    rmtree(workflow_dir)


def test_update_workflow(client, app, workflow):
    resp = login_user(client)
    assert "access_token" in resp.json
    headers = {"X-API-KEY": resp.json.get("access_token")}
    workflow_id = str(workflow.id)

    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}'

    data = {
        "name": "new name",
        "structure": {"nodes": [], "edges": []},
        "base64_img": "asdfasdfasdg",
    }
    resp = client.put(
        f"/api/workflow/{workflow.id}",
        content_type="application/json",
        headers=headers,
        data=json.dumps(data),
    )

    logging.info(f"Removing workflow directory {workflow_dir}")
    rmtree(workflow_dir)
    assert resp.status_code == 200
    assert resp.json.get("message") == "workflow edited"


def test_delete_workflow(app, client, workflow):
    resp = login_user(client)
    assert "access_token" in resp.json
    headers = {"X-API-KEY": resp.json.get("access_token")}
    workflow_id = str(workflow.id)
    workflow_dir = f'{app.config["FALCOEYE_ASSETS"]}/workflows/{workflow_id}'
    logging.info(f"Removing workflow directory {workflow_dir}")

    rmtree(workflow_dir)

    resp = client.delete(f"/api/workflow/{workflow.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "workflow deleted"


def test_empty_workflows(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/workflow/", headers=headers)
    assert resp.status_code == 204


def test_get_invalid_workflow_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/workflow/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "workflow not found"


def test_delete_invalid_workflow_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/workflow/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "workflow not found"
