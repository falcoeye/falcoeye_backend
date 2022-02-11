from .utils import login_user, register_user


def test_auth_register_login(client, db):
    resp = register_user(client)
    assert 201 == resp.status_code
    assert "access_token" in resp.json

    resp = login_user(client)
    assert resp.status_code == 200
    assert "access_token" in resp.json
