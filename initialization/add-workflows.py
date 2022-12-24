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

URL = "http://localhost:3000"
# URL = "https://falcoeye-backend-xbjr6s7buq-uc.a.run.app"

workflow_user = os.getenv("WORKFLOW_USER").strip()
workflow_password = os.getenv("WORKFLOW_PASSWORD").strip()
payload = {"email": workflow_user, "password": workflow_password}
resp = requests.post(f"{URL}/auth/login", json=payload)
headers = {
    "X-API-KEY": f'JWT {resp.json().get("access_token")}',
    "content_type": "application/json",
}
user_id = resp.json().get("user").get("id")
workflows = glob.glob(f"{basedir}/workflows/*.json")
workflows += glob.glob(f"{basedir}/inline_workflows/*.json")


def update(wfid, data):

    resp = requests.put(f"{URL}/api/workflow/{wfid}", headers=headers, json=data)
    logging.info(resp.json())


def get_base64img(imgfile):
    with open(imgfile, "rb") as image_file:
        data = base64.b64encode(image_file.read())
    return data.decode("utf-8")


# TODO: what after 100?!!
resp = requests.get(f"{URL}/api/workflow/?per_page=100", headers=headers)
if resp.status_code != 204:
    s_workflows = resp.json()["workflow"]
else:
    s_workflows = []

resp = requests.get(f"{URL}/api/workflow/?per_page=100&inline=true", headers=headers)
if resp.status_code != 204:
    s_workflows += resp.json()["workflow"]


logging.info(s_workflows)


def add(data):
    resp = requests.post(f"{URL}/api/workflow/", json=data, headers=headers)
    logging.info(resp.json())
    assert resp.status_code == 201


logging.info("Deleting bad workflows")
for sw in s_workflows:
    found = False
    for wf in workflows:
        with open(wf) as f:
            wkflowdict = json.load(f)
        if sw["name"] == wkflowdict["name"]:
            found = True
            break
    if not found:
        logging.info(f"Deleting {sw['id']}")
        resp = requests.delete(f"{URL}/api/workflow/{sw['id']}", headers=headers)
        logging.info(resp.json())


for wf in workflows:
    logging.info(f"Loading {wf}")
    with open(wf) as f:
        wkflowdict = json.load(f)

    # if wkflowdict["name"] == "Arabian Angelfish Monitor":
    #     delete(wkflowdict)

    logging.info(f"Adding workflow {wkflowdict['name']}")

    data = {
        "name": wkflowdict["name"],
        "creator": user_id,
        "structure": wkflowdict["structure"],
        "usedfor": wkflowdict["usedfor"],
        "consideration": wkflowdict["consideration"],
        "assumption": wkflowdict["assumption"],
        "results_description": wkflowdict["results_description"],
    }
    if os.path.exists(wf.replace(".json", ".jpg")):
        base64img = get_base64img(wf.replace(".json", ".jpg"))
        data["image"] = base64img

    done = False
    for sw in s_workflows:
        if sw["name"] == wkflowdict["name"]:
            logging.info("Workflow exists. Updating")
            update(sw["id"], data)
            logging.info(f"{wkflowdict['name']} updated")
            done = True
            break

    if not done:
        add(data)
        logging.info(f"{wkflowdict['name']} added")
