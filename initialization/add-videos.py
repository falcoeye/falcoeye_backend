import base64
import glob
import json
import logging
import os

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

basedir = os.path.abspath(os.path.dirname(__file__))
videodir = f"{basedir}/../../media"


def add(data, filename):
    files = {"file": open(f"{videodir}/{filename}", "rb")}
    file_headers = {
        "X-API-KEY": headers["X-API-KEY"],
        "content_type": "multipart/form-data",
    }
    resp = requests.post(f"{URL}/api/upload", headers=file_headers, files=files)
    assert resp.status_code == 200
    assert "registry_key" in resp.json()
    data["registry_key"] = resp.json()["registry_key"]
    logging.info(f'Registry key: {data["registry_key"]}')
    resp = requests.post(f"{URL}/api/media/video", json=data, headers=headers)
    assert resp.status_code == 201
    logging.info(resp.json())


def update(vidid, data):
    resp = requests.put(f"{URL}/api/media/video/{vidid}", headers=headers, json=data)
    assert resp.status_code == 200
    logging.info(resp.json())


URL = "http://localhost:3000"

test_user = "falcoeye-test@falcoeye.io"
test_password = "falcoeye-test"
payload = {"email": test_user, "password": test_password}
resp = requests.post(f"{URL}/auth/login", json=payload)
headers = {
    "X-API-KEY": f'JWT {resp.json().get("access_token")}',
    "content_type": "application/json",
}

resp = requests.get(f"{URL}/api/media/?per_page=100", headers=headers)
if resp.status_code != 204:
    s_videos = resp.json()["media"]
else:
    s_videos = []


logging.info(s_videos)

with open(f"{basedir}/videos/videos.json") as f:
    videos = json.load(f)

logging.info("Deleting bad videos")
for sv in s_videos:
    found = False
    for vid in videos:
        if sv["note"] == vid["note"]:
            found = True
            break
    if not found:
        logging.info(f"Deleting {sv['id']}")
    resp = requests.delete(f"{URL}/api/media/video/{sv['id']}", headers=headers)
    logging.info(resp.json())

for sv in videos:
    logging.info(f"Adding {sv['note']}")
    data = {"tags": sv["tags"], "note": sv["note"], "camera_id": sv["camera_id"]}

    done = False
    for sv_ in s_videos:
        if sv_["note"] == sv["note"]:
            logging.info("Source exists. Updating")
            update(sv_["id"], data)
            logging.info(f"{sv_['note']} updated")
            done = True
            break

    if not done:
        add(data, sv["filename"])
        logging.info(f"{sv['note']} added")
