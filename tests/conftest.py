import flask_migrate
import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    with app.app_context():
        with app.test_client() as client:
            flask_migrate.upgrade()
            yield client
