"""Shared functions and constants for unit tests."""

import json

EMAIL = "dummy_user@dummy.com"
USERNAME = "dummy.User"
PASSWORD = "test1234"


def register_user(test_client, email=EMAIL, password=PASSWORD, username=USERNAME):
    return test_client.post(
        "/auth/register",
        data=json.dumps(dict(email=email, password=password, username=username)),
        content_type="application/json",
    )


def login_user(test_client, email=EMAIL, password=PASSWORD):
    return test_client.post(
        "/auth/login",
        data=json.dumps(dict(email=email, password=password)),
        content_type="application/json",
    )


def get_user(test_client, access_token):
    return test_client.get(
        "/api/user/profile", headers={"Authorization": f"X-API-TOKEN {access_token}"}
    )
