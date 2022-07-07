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

URL = "http://localhost:5000"

workflow_user = os.getenv("WORKFLOW_USER").strip()
workflow_password = os.getenv("WORKFLOW_PASSWORD").strip()
payload = {"email": workflow_user, "password": workflow_password}
resp = requests.post(f"{URL}/auth/login", json=payload)
headers = {
    "X-API-KEY": resp.json().get("access_token"),
    "content_type": "application/json",
}
workflows = glob.glob(f"{basedir}/workflows/*.json")

for wf in workflows:

    with open(wf) as f:
        wkflowdict = json.load(f)

    logging.info(f"Adding workflow {wkflowdict['name']}")
    data = {
        "name": wkflowdict["name"],
        "creator": resp.json().get("user").get("id"),
        "structure": wkflowdict["structure"],
        "usedfor": wkflowdict["usedfor"],
        "consideration": wkflowdict["consideration"],
        "assumption": wkflowdict["assumption"],
        "results_description": wkflowdict["results_description"],
    }

    resp = requests.post(f"{URL}/api/workflow/", json=data, headers=headers)
    logging.info(resp.json())
    assert resp.status_code == 201 or resp.status_code == 403
    # assert resp.json().get("message") == "workflow added"
    logging.info(f"{wkflowdict['name']} added")
