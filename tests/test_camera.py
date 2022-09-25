import base64
import json
import logging
import os
import uuid

from app.dbmodels.schemas import CameraSchema

from .utils import login_user

camera_schema = CameraSchema()


def get_base64img(imgfile):
    with open(imgfile, "rb") as image_file:
        data = base64.b64encode(image_file.read())
    return data.decode("utf-8")


basedir = os.path.abspath(os.path.dirname(__file__))


def test_add_camera(client, user):  # , manufacturer):
    resp = login_user(client)
    assert "access_token" in resp.json

    access_token = resp.json.get("access_token")
    headers = {"X-API-KEY": access_token}

    data = {
        "name": "Harbour Village Bonaire Coral Reef",
        # "manufacturer_id": str(manufacturer.id),
        "streaming_type": "StreamingServer",
        "url": "https://www.youtube.com/watch?v=tk-qJJbdOh4",
        "status": "RUNNING",
    }
    resp = client.post(
        "/api/camera/",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "camera added"

    resp = client.get("/api/camera/", headers=headers)
    assert (
        resp.json.get("camera")[0].get("name") == "Harbour Village Bonaire Coral Reef"
    )
    assert resp.json.get("message") == "camera data sent"
    assert resp.status_code == 200


def test_add_camera_with_img(client, user):  # , manufacturer):
    resp = login_user(client)
    assert "access_token" in resp.json

    access_token = resp.json.get("access_token")
    headers = {"X-API-KEY": access_token}

    data = {
        "name": "Harbour Village Bonaire Coral Reef",
        # "manufacturer_id": str(manufacturer.id),
        "streaming_type": "StreamingServer",
        "url": "https://www.youtube.com/watch?v=tk-qJJbdOh4",
        "status": "RUNNING",
    }
    base64img = get_base64img(f"{basedir}/media/fish.jpg")
    data["image"] = base64img
    resp = client.post(
        "/api/camera/",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json",
    )
    assert resp.status_code == 201
    assert resp.json.get("message") == "camera added"

    resp = client.get("/api/camera/", headers=headers)
    assert (
        resp.json.get("camera")[0].get("name") == "Harbour Village Bonaire Coral Reef"
    )
    assert resp.json.get("message") == "camera data sent"
    assert resp.status_code == 200


def test_list_cameras(client, camera):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/camera/", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "camera data sent"


def test_list_camera_count(client, camera):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/camera/count", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "camera count data sent"
    assert resp.json.get("camera_count") == 1


def test_empty_cameras(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/camera/", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("lastPage")


def test_get_camera_by_id(client, camera):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/camera/{camera.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("camera").get("name") == camera.name
    assert resp.json.get("message") == "camera data sent"


def test_get_invalid_camera_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/camera/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "camera not found"


def test_delete_camera_by_id(client, camera):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/camera/{camera.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "camera deleted"


def test_delete_invalid_camera_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/camera/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "camera not found"


def test_update_camera_by_id(client, camera):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    camera.name = "UpdatedCamera"
    camera_json = camera_schema.dump(camera)
    base64img = get_base64img(f"{basedir}/media/fish.jpg")
    camera_json["image"] = base64img
    resp = client.put(
        f"/api/camera/{camera.id}",
        headers=headers,
        data=json.dumps(camera_json),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.json.get("message") == "camera edited"

    resp = client.get(f"/api/camera/{camera.id}", headers=headers)
    logging.info(resp.json)
    assert resp.status_code == 200
    assert resp.json.get("camera").get("name") == "UpdatedCamera"


# def test_list_manufacturers(client, user, manufacturer):
#     resp = login_user(client)
#     headers = {"X-API-KEY": resp.json.get("access_token")}
#     resp = client.get("/api/manufacturer/", headers=headers)
#     assert resp.status_code == 200
#     assert resp.json.get("manufacturer")[0].get("name") == manufacturer.name
#     assert resp.json.get("message") == "Manufacturer data sent"


# def test_empty_manufacturers(client, user):
#     resp = login_user(client)
#     headers = {"X-API-KEY": resp.json.get("access_token")}
#     resp = client.get("/api/manufacturer/", headers=headers)
#     assert resp.status_code == 404


# def test_create_manufacturer(client, user):
#     resp = login_user(client)
#     headers = {"X-API-KEY": resp.json.get("access_token")}
#     data = {"name": "dummy manufacturer"}
#     resp = client.post(
#         "/api/manufacturer/",
#         data=json.dumps(data),
#         content_type="application/json",
#         headers=headers,
#     )
#     assert resp.status_code == 201
#     assert resp.json.get("message") == "Manufacturer has been added"

#     resp = client.get("/api/manufacturer/", headers=headers)
#     assert resp.json.get("manufacturer")[0].get("name") == "dummy manufacturer"
#     assert resp.json.get("message") == "Manufacturer data sent"
#     assert resp.status_code == 200


# def test_create_duplicate_manufacturer(client, user, manufacturer):
#     resp = login_user(client)
#     headers = {"X-API-KEY": resp.json.get("access_token")}
#     data = {"name": manufacturer.name}
#     resp = client.post(
#         "/api/manufacturer/",
#         data=json.dumps(data),
#         content_type="application/json",
#         headers=headers,
#     )
#     assert resp.status_code == 403
#     assert resp.json.get("message") == "Manufacturer does exist"


# def test_get_manufacturer_by_name(client, user, manufacturer):
#     # TODO
#     pass


# def test_get_manufacturer_by_id(client, user, manufacturer):
#     resp = login_user(client)
#     headers = {"X-API-KEY": resp.json.get("access_token")}
#     resp = client.get(f"/api/manufacturer/{manufacturer.id}", headers=headers)
#     assert resp.status_code == 200
#     assert resp.json.get("message") == "Manufacturer data sent"
#     assert resp.json.get("manufacturer").get("name") == manufacturer.name


# def test_get_invalid_manufacturer_by_id(client, user):
#     resp = login_user(client)
#     headers = {"X-API-KEY": resp.json.get("access_token")}
#     resp = client.get(f"/api/manufacturer/{uuid.uuid4()}", headers=headers)
#     assert resp.status_code == 404
#     assert resp.json.get("message") == "Manufacturer not found!"


# def test_delete_manufacturer(client, user, manufacturer):
#     resp = login_user(client)
#     headers = {"X-API-KEY": resp.json.get("access_token")}
#     resp = client.delete(f"/api/manufacturer/{manufacturer.id}", headers=headers)
#     assert resp.status_code == 200
#     assert resp.json.get("message") == "Manufacturer deleted"


# def test_delete_invalid_manufacturer(client, user):
#     resp = login_user(client)
#     headers = {"X-API-KEY": resp.json.get("access_token")}
#     resp = client.delete(f"/api/manufacturer/{uuid.uuid4()}", headers=headers)
#     assert resp.status_code == 404
#     assert resp.json.get("message") == "Manufacturer not found!"


# def test_update_manufacturer(client, user, manufacturer):
#     # TODO
#     pass
