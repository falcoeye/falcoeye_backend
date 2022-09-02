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

# URL = "https://falcoeye-backend-xbjr6s7buq-uc.a.run.app"
URL = "http://localhost:8000"
workflow_user = os.getenv("WORKFLOW_USER").strip()
workflow_password = os.getenv("WORKFLOW_PASSWORD").strip()
payload = {"email": workflow_user, "password": workflow_password}
resp = requests.post(f"{URL}/auth/login", json=payload)
headers = {
    "X-API-KEY": f'JWT {resp.json().get("access_token")}',
    "content_type": "application/json",
}

resp = requests.get(f"{URL}/api/capture", headers=headers)
logging.info(resp.status_code)
s_registry = resp.json()["registry"]
logging.info(s_registry)

for m in s_registry:
    logging.info(f"Deleting {m['id']}")
    resp = requests.delete(f"{URL}/api/capture/{m['id']}", headers=headers)
    logging.info(resp.status_code)
