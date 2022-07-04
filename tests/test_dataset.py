import json
import uuid

from .utils import login_user


def test_delete_dataset(client, dataset):
    resp = login_user(client)
    assert "access_token" in resp.json
    headers = {"X-API-KEY": resp.json.get("access_token")}

    resp = client.delete(f"/api/dataset/{dataset.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "dataset deleted"


def test_add_dataset(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    data = {
        "name": "dummy dataset in test",
        "annotation_type": "DummyType",
        "creator": str(user.id),
        "image_width": 1920,
        "image_height": 1080,
        "size_type": "DummySizeType",
    }
    resp = client.post(
        "/api/dataset/",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "dataset added"


def test_list_datasets(client, dataset):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/dataset/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json.get("dataset")) == 1
    assert resp.json.get("message") == "dataset data sent"
