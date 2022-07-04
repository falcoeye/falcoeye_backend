import datetime
import json
import uuid

from .utils import login_user


def test_list_aimodel(client, aimodel):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/aimodel/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json.get("aimodel")) == 1
    assert resp.json.get("message") == "aimodel data sent"


def test_add_aimodel(client, user, dataset):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    data = {
        "name": "FourtyThreeFish",
        "creator": str(user.id),
        "architecture": "frcnn",
        "backbone": "resnet50",
        "dataset_id": str(dataset.id),
        "technology": "tensorflow",
        "speed": 1,
    }
    resp = client.post(
        "/api/aimodel/",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "aimodel added"


def test_delete_aimodel(client, aimodel):
    resp = login_user(client)
    assert "access_token" in resp.json
    headers = {"X-API-KEY": resp.json.get("access_token")}

    resp = client.delete(f"/api/aimodel/{aimodel.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "aimodel deleted"


def test_empty_aimodels(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/aimodel/", headers=headers)
    assert resp.status_code == 404


def test_get_invalid_aimodel_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/aimodel/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "aimodel not found"


def test_delete_invalid_aimodel_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/aimodel/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "aimodel not found"
