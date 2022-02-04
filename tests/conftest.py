import os

import pytest
from flask_migrate import Migrate

from app import create_app, db


@pytest.fixture
def client():
    app = create_app(os.getenv("FLASK_CONFIG") or "default")
    migrate = Migrate(app, db)
    with app.test_client() as client:
        yield client
