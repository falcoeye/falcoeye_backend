import os

import click
from app import create_app
from app import db
from app.dbmodels import *
from config import config_by_name
from flask_migrate import Migrate


app = create_app(os.getenv("FLASK_CONFIG") or "default")

migrate = Migrate(app, db)
