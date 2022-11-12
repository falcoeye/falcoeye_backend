import logging
import os
import os.path
import random
import shutil
import string
from datetime import datetime, timedelta

import google.auth
from flask import current_app
from google.auth import compute_engine
from google.auth.transport import requests as grequests
from google.cloud import storage
from PIL import Image


def message(status, message):
    response_object = {"status": status, "message": message}
    return response_object


def validation_error(status, errors):
    response_object = {"status": status, "errors": errors}

    return response_object


def random_string(N=6):
    randomstr = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(N)
    )
    logging.info(f"random_string called with N={N}: returning {randomstr}")
    return randomstr


def err_resp(msg, reason, code):
    err = message(False, msg)
    err["error_reason"] = reason
    return err, code


def internal_err_resp():
    err = message(False, "Something went wrong during the process!")
    err["error_reason"] = "server_error"
    return err, 500


def mkdir(path):
    path = os.path.relpath(path)
    if current_app.config["FS_OBJ"].isdir(path):
        return
    if current_app.config["FS_IS_REMOTE"]:
        if not path.endswith("/"):
            path = path + "/"
        current_app.config["FS_OBJ"].touch(path)
    else:
        current_app.config["FS_OBJ"].makedirs(path)


def rmtree(path):
    path = path.replace("//", "/")
    path = os.path.relpath(path)
    if not path.endswith("/"):
        path = path + "/"
    if not current_app.config["FS_OBJ"].isdir(path):
        return
    if current_app.config["FS_IS_REMOTE"]:
        current_app.config["FS_OBJ"].delete(path, recursive=True)
    else:
        shutil.rmtree(path)


def move(src, dst):
    src = os.path.relpath(src)
    dst = os.path.relpath(dst)

    if current_app.config["FS_IS_REMOTE"]:
        current_app.config["FS_OBJ"].move(src, dst)
    else:
        shutil.move(src, dst)


def put(f_from, f_to):
    f_from = os.path.relpath(f_from)
    f_to = os.path.relpath(f_to)

    if current_app.config["FS_IS_REMOTE"]:
        current_app.config["FS_OBJ"].put(f_from, f_to)
    else:
        shutil.copy2(f_from, f_to)


def exists(path):
    path = path.replace("//", "/")
    if current_app.config["FS_IS_REMOTE"]:
        return current_app.config["FS_OBJ"].exists(path)
    else:
        return os.path.exists(path)


def generate_download_signed_url_v4(bucket_name, blob_name, expiration):

    blob_name = blob_name.replace("//", "/")
    if bucket_name is None or bucket_name.strip() == "":
        # running localy
        return blob_name

    if blob_name[0] == "/":
        blob_name = blob_name[1:]
    # multiple // in the blob will not generate a correct link
    if blob_name[0] == "/":
        blob_name = blob_name[1:]
    blob_name = blob_name.replace("//", "/")
    bucket_name = bucket_name.strip("/")

    credentials, project_id = google.auth.default()
    r = grequests.Request()
    credentials.refresh(r)

    storage_client = storage.Client()
    logging.info("Storage client created")

    bucket = storage_client.get_bucket(bucket_name)

    blob = bucket.blob(blob_name)
    expires = datetime.now() + timedelta(seconds=expiration * 60)

    service_account_email = credentials.service_account_email
    logging.info(
        f"Generating signed url with {service_account_email} account for blob {blob_name} and bucket {bucket}"
    )

    url = blob.generate_signed_url(
        expiration=expires,
        service_account_email=service_account_email,
        access_token=credentials.token,
    )
    return url


def get_service(service_name):
    if (
        current_app.config["DEPLOYMENT"] == "gcloud"
        or current_app.config["DEPLOYMENT"] == "local"
    ):
        return os.environ.get(current_app.config["SERVICES"][service_name]["env"])
    elif current_app.config["DEPLOYMENT"] == "k8s":
        return (
            "http://"
            + current_app.config["SERVICES"][service_name]["k8s"].get_service_address()
        )
