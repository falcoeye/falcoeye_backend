import json
import logging
import uuid

from app.utils import rmtree

from .utils import login_user


def test_list_media_1(client, image, video):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/media/", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "media data sent"


def test_list_media_paged(client, app, user, registry_image, camera):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    logging.info("Adding 11 images")
    for i in range(11):

        data = {
            "registry_key": str(registry_image.id),
            "note": "test_notes",
            "tags": "test_tags",
            "camera_id": str(camera.id),
            "media_type": "image",
        }

        resp = client.post(
            "/api/media/image",
            headers=headers,
            data=json.dumps(data),
            content_type="application/json",
        )

        # 417 because DB object will be created, but the request will fail due to
        # registry item already moved.
        assert resp.status_code == 201 or resp.status_code == 417
        # assert resp.json.get("message") == "image added"

    resp = client.get("/api/media/", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "media data sent"
    assert len(resp.json.get("media")) == 10

    user_temp_dir = f"{app.config['TEMPORARY_DATA_PATH']}/{user.id}"
    user_asset_dir = f"{app.config['USER_ASSETS']}/{user.id}"
    rmtree(user_temp_dir)
    rmtree(user_asset_dir)


def test_list_media_count(client, image, video):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/media/count", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "media count data sent"
    assert resp.json.get("media_count") == 2


def test_add_image(app, client, user, registry_image, camera):
    resp = login_user(client)
    assert "access_token" in resp.json

    access_token = resp.json.get("access_token")
    headers = {"X-API-KEY": access_token}
    data = {
        "registry_key": str(registry_image.id),
        "note": "test_notes",
        "tags": "test_tags",
        "camera_id": str(camera.id),
    }

    resp = client.post(
        "/api/media/image",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json",
    )

    assert resp.status_code == 201
    assert resp.json.get("message") == "image added"

    resp = client.get("/api/media/", headers=headers)
    assert resp.json.get("media")[0].get("camera_id") == str(camera.id)
    assert resp.status_code == 200
    assert resp.json.get("message") == "media data sent"
    user_temp_dir = f"{app.config['TEMPORARY_DATA_PATH']}/{user.id}"
    user_asset_dir = f"{app.config['USER_ASSETS']}/{user.id}"
    rmtree(user_temp_dir)
    rmtree(user_asset_dir)


def test_empty_media(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/media/", headers=headers, content_type="application/json")

    assert resp.status_code == 200
    # TODO: Why cannot access data


def test_get_image_by_id(client, harbour_camera, image):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/media/image/{image.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("image").get("camera_id") == str(harbour_camera.id)
    assert resp.json.get("message") == "image data sent"


def test_get_invalid_image_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/media/image/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "image not found"


def test_delete_image_by_id(client, user, image):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/media/image/{image.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "image deleted"


def test_edit_image_by_id(client, user, image):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    data = {"tags": "new_tags", "note": "new_note"}
    resp = client.put(
        f"/api/media/image/{image.id}",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json",
    )
    resp = client.get(f"/api/media/image/{image.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("image")["note"] == "new_note"
    assert resp.json.get("image")["tags"] == "new_tags"


def test_delete_invalid_image_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/media/image/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "image not found"


def test_add_video(app, client, user, registry_video, camera):
    resp = login_user(client)
    assert "access_token" in resp.json

    access_token = resp.json.get("access_token")
    headers = {"X-API-KEY": access_token}
    data = {
        "registry_key": str(registry_video.id),
        "camera_id": str(camera.id),
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
    assert resp.json.get("message") == "video added"

    resp = client.get("/api/media/", headers=headers)
    assert resp.json.get("media")[0].get("camera_id") == str(camera.id)
    assert resp.status_code == 200
    assert resp.json.get("message") == "media data sent"

    user_temp_dir = f"{app.config['TEMPORARY_DATA_PATH']}/{user.id}"
    user_asset_dir = f"{app.config['USER_ASSETS']}/{user.id}"
    rmtree(user_temp_dir)
    rmtree(user_asset_dir)


def test_list_media_2(client, image, video):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get("/api/media/", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("message") == "media data sent"


def test_get_video_by_id(client, harbour_camera, video):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/media/video/{video.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("video").get("camera_id") == str(harbour_camera.id)
    assert resp.json.get("message") == "video data sent"


def test_get_invalid_video_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.get(f"/api/media/video/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "video not found"


def test_delete_video_by_id(client, user, video):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/media/video/{video.id}", headers=headers)
    # 204 because in this test no real video added
    assert resp.status_code == 200
    assert resp.json.get("message") == "video deleted"


def test_edit_video_by_id(client, user, video):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    data = {"tags": "new_tags", "note": "new_note"}
    resp = client.put(
        f"/api/media/video/{video.id}",
        headers=headers,
        data=json.dumps(data),
        content_type="application/json",
    )
    resp = client.get(f"/api/media/video/{video.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json.get("video")["note"] == "new_note"
    assert resp.json.get("video")["tags"] == "new_tags"


def test_delete_invalid_video_by_id(client, user):
    resp = login_user(client)
    headers = {"X-API-KEY": resp.json.get("access_token")}
    resp = client.delete(f"/api/media/video/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404
    assert resp.json.get("message") == "video not found"
