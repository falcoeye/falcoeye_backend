import json
import os

from .conftest import client
from .test_auth import login


def test_add_image(client):

    token = login(client)
    headers = {"X-API-KEY": token}

    rv = client.post("/api/media/add_image test1 1 test1 test1 1", headers=headers)
    data = json.loads(rv.data.decode("utf-8"))
    assert data["message"] == "Image has been added."

    rv = client.post("/api/media/delete_image test1", headers=headers)
    data = json.loads(rv.data.decode("utf-8"))
    assert data["message"] == "Image has been deleted."
