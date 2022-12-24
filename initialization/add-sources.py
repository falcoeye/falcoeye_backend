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


def add(data):
    resp = requests.post(f"{URL}/api/camera/", json=data, headers=headers)
    logging.info(resp.json())
    assert resp.status_code == 201


def update(wfid, data):

    resp = requests.put(f"{URL}/api/camera/{wfid}", headers=headers, json=data)
    logging.info(resp.json())


def get_base64img(imgfile):
    with open(imgfile, "rb") as image_file:
        data = base64.b64encode(image_file.read())
    return data.decode("utf-8")


URL = "http://localhost:3000"

test_user = "falcoeye-test@falcoeye.io"
test_password = "falcoeye-test"
payload = {"email": test_user, "password": test_password}
resp = requests.post(f"{URL}/auth/login", json=payload)
headers = {
    "X-API-KEY": f'JWT {resp.json().get("access_token")}',
    "content_type": "application/json",
}

resp = requests.get(f"{URL}/api/camera/?per_page=100", headers=headers)
if resp.status_code != 204 and "camera" in resp.json():
    s_sources = resp.json()["camera"]
else:
    s_sources = []


logging.info(s_sources)

with open(f"{basedir}/sources/sources.json") as f:
    sources = json.load(f)

logging.info("Deleting bad sources")
for ss in s_sources:
    found = False
    for src in sources:
        if ss["name"] == src["name"]:
            found = True
            break
    if not found:
        logging.info(f"Deleting {ss['id']}")
        resp = requests.delete(f"{URL}/api/camera/{ss['id']}", headers=headers)
        logging.info(resp.json())

for ss in sources:
    logging.info(f"Addings {ss['name']}")
    if ss["streaming_type"] == "StreamingServer":
        data = {
            "name": ss["name"],
            "streaming_type": "StreamingServer",
            "url": ss["url"],
            "status": "RUNNING",
            "latitude": ss["latitude"],
            "longitude": ss["longitude"],
        }
    else:
        pass

    if os.path.exists(f'{basedir}/sources/{ss["thumbnail"]}'):
        base64img = get_base64img(f'{basedir}/sources/{ss["thumbnail"]}')
        data["image"] = base64img

    done = False
    for ss_ in s_sources:
        if ss_["name"] == ss["name"]:
            logging.info("Source exists. Updating")
            update(ss_["id"], data)
            logging.info(f"{ss_['name']} updated")
            done = True
            break

    if not done:
        add(data)
        logging.info(f"{ss['name']} added")
