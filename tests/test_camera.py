import json
import uuid

from .utils import login_user


def test_add_camera(client, user, manufacturer, streamer):
    resp = login_user(client)
    assert "access_token" in resp.json

    access_token = resp.json.get("access_token")
    headers = {"X-API-KEY": access_token}

    data = {
        "name": "dummy camera",
        "manufacturer_id": str(manufacturer.id),
        "streamer_id": str(streamer.id),
        "url": "https://test.test.com",
        "owner_id": user.id,
        "status": "RUNNING",
    }
    resp = client.post(
        "/api/camera/",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "Camera has been added"

    resp = client.get("/api/camera/", headers=headers)
    assert resp.json.get("camera")[0].get("name") == "dummy camera"
    assert resp.json.get("message") == "Camera data sent"
    assert resp.status_code == 200


def test_list_cameras(client, camera):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/camera/", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "Camera data sent"


def test_empty_cameras(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/camera/", headers=headers)
    assert resp.status_code == 404


def test_get_camera_by_id(client, camera):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/camera/{camera.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("camera").get("name") == camera.name
    assert resp.json.get("message") == "Camera data sent"


def test_get_invalid_camera_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/camera/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "Camera not found!"


def test_delete_camera_by_id(client, camera):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/camera/{camera.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "Camera deleted"


def test_delete_invalid_camera_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/camera/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "Camera not found!"


def test_update_camera_by_id(client, camera):
    # TODO
    pass


def test_list_manufacturers(client, user, manufacturer):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/manufacturer/", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("manufacturer")[0].get("name") == manufacturer.name
    assert resp.json.get("message") == "Manufacturer data sent"


def test_empty_manufacturers(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/manufacturer/", headers=headers)
    assert resp.status_code == 404


def test_create_manufacturer(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    data = {"name": "dummy manufacturer"}
    resp = client.post(
        "/api/manufacturer/",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "Manufacturer has been added"

    resp = client.get("/api/manufacturer/", headers=headers)
    assert resp.json.get("manufacturer")[0].get("name") == "dummy manufacturer"
    assert resp.json.get("message") == "Manufacturer data sent"
    assert resp.status_code == 200


def test_create_duplicate_manufacturer(client, user, manufacturer):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    data = {"name": manufacturer.name}
    resp = client.post(
        "/api/manufacturer/",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 403
    assert resp.json.get("message") == "Manufacturer does exist"


def test_get_manufacturer_by_name(client, user, manufacturer):
    # TODO
    pass


def test_get_manufacturer_by_id(client, user, manufacturer):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/manufacturer/{manufacturer.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "Manufacturer data sent"
    assert resp.json.get("manufacturer").get("name") == manufacturer.name


def test_get_invalid_manufacturer_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/manufacturer/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "Manufacturer not found!"


def test_delete_manufacturer(client, user, manufacturer):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/manufacturer/{manufacturer.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "Manufacturer deleted"


def test_delete_invalid_manufacturer(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/manufacturer/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "Manufacturer not found!"


def test_update_manufacturer(client, user, manufacturer):
    # TODO
    pass
