import json
import os
import uuid

from .utils import login_user


def test_add_image(client, db, user):
    resp = login_user(client)
    assert "access_token" in resp.json


def test_add_image(client, user, harbourcamera):
    resp = login_user(client)
    assert "access_token" in resp.json

    access_token = resp.json.get("access_token")
    headers = {"X-API-KEY": access_token}
    data = {
        "camera_id": str(harbourcamera.id),
        "note": "test_notes",
        "tags": "test_tags",
    }

    resp = client.post(
        "/api/media/image",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json",
    )

    assert resp.status_code == 201
    assert resp.json.get("message") == "Image has been added"

    resp = client.get("/api/media/", headers=headers)
    assert resp.json.get("media")[0].get("camera_id") == str(harbourcamera.id)
    assert resp.status_code == 200
    assert resp.json.get("message") == "User media sent"


def test_list_media_1(client, image):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/media/", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "User media sent"


def test_empty_media(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/media/", headers=headers, content_type="application/json")

    assert resp.status_code == 204
    # TODO: Why cannot access data


def test_get_image_by_id(client, harbourcamera, image):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/media/image/{image.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("image").get("camera_id") == str(harbourcamera.id)
    assert resp.json.get("message") == "Image data sent"


def test_get_invalid_image_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/media/image/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "Image not found!"


def test_delete_image_by_id(client, user, image):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/media/image/{image.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "Image deleted"


def test_delete_invalid_image_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/media/image/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "Image not found!"


# def test_update_image_by_id(client, camera):
#     # TODO
#     pass


def test_add_video(client, user, harbourcamera):
    resp = login_user(client)
    assert "access_token" in resp.json

    access_token = resp.json.get("access_token")
    headers = {"X-API-KEY": access_token}
    data = {
        "camera_id": str(harbourcamera.id),
        "note": "test_notes",
        "tags": "test_tags",
        "duration": 10,
    }

    resp = client.post(
        "/api/media/video",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json",
    )

    assert resp.status_code == 201
    assert resp.json.get("message") == "Video has been added"

    resp = client.get("/api/media/", headers=headers)
    assert resp.json.get("media")[0].get("camera_id") == str(harbourcamera.id)
    assert resp.status_code == 200
    assert resp.json.get("message") == "User media sent"


def test_list_media_2(client, image, video):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/media/", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "User media sent"


def test_get_video_by_id(client, harbourcamera, video):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/media/video/{video.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("video").get("camera_id") == str(harbourcamera.id)
    assert resp.json.get("message") == "Video data sent"


def test_get_invalid_image_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/media/video/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "Video not found!"


def test_delete_video_by_id(client, user, video):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/media/video/{video.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "Video deleted"


def test_delete_invalid_video_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/media/video/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "Video not found!"
