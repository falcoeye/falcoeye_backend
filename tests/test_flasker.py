

import os
import sys
sys.path.insert(0,"../")
import tempfile

import pytest
import json
from app import create_app
from app import db
from app.dbmodels import *
from config import config_by_name
from flask_migrate import Migrate


@pytest.fixture
def client():
    app = create_app(os.getenv("FLASK_CONFIG") or "default")
    migrate = Migrate(app, db)
    with app.test_client() as client:
        yield client

