import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, f"{basedir}/../")
from app import create_app
from app.dbmodels import Role

print(os.getenv("FLASK_CONFIG"))
app = create_app(os.getenv("FLASK_CONFIG") or "default")

with app.app_context():
    print("inserting roles ...")
    Role.insert_roles()
