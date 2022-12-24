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

# URL = "https://falcoeye-backend-xbjr6s7buq-uc.a.run.app"
URL = "http://localhost:3000"

user = os.getenv("FALCOEYE_USER").strip()
password = os.getenv("FALCOEYE_PASSWORD").strip()
payload = {"email": user, "password": password}
resp = requests.post(f"{URL}/auth/login", json=payload)
headers = {
    "X-API-KEY": f'JWT {resp.json().get("access_token")}',
    "content_type": "application/json",
}

# resp = requests.get(f"{URL}/api/media/", headers=headers)
# s_media = resp.json()["media"]
# logging.info(s_media)

# for m in s_media:
#     logging.info(f"Deleting {m['id']}")
#     if m["media_type"] == "image":
#         resp = requests.delete(f"{URL}/api/media/image/{m['id']}", headers=headers)
#     elif m["media_type"] == "video":
#         resp = requests.delete(f"{URL}/api/media/video/{m['id']}", headers=headers)

resp = requests.get(f"{URL}/api/analysis/", headers=headers)
print(resp.json())
s_media = resp.json()["analysis"]
logging.info(s_media)

for m in s_media:
    logging.info(f"Deleting {m['id']}")
    # if m["id"] == "3ccf378e-53f7-4ed8-8f95-ca7b1231dd4f":
    resp = requests.delete(f"{URL}/api/analysis/{m['id']}", headers=headers)
    logging.info(resp.status_code)
