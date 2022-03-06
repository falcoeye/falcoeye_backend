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
        "creator": 0,
        "image_width": 1920,
        "image_height": 1080,
        "size_type": "DummySizeType",
    }
    resp = client.post(
        "/api/workflow/",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "Dataset has been added"

    # resp = client.get("/api/manufacturer/", headers=headers)
    # assert resp.json.get("manufacturer")[0].get("name") == "dummy manufacturer"
    # assert resp.json.get("message") == "Manufacturer data sent"
    # assert resp.status_code == 200
