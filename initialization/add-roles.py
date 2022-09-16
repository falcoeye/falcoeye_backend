import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, f"{basedir}/../")
from app import create_app
from app.dbmodels import Role

print(os.getenv("FLASK_CONFIG"))
app = create_app(os.getenv("FLASK_CONFIG") or "default")

with app.app_context():
    print("inserting roles ...")
    Role.insert_roles()
    roles = Role.query.all()
    for r in roles:
        logging.info(f"Role {r.name}: {r.permissions}")
