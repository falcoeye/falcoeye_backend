import os

from app import create_app
from app.dbmodels import Role

print(os.getenv("FLASK_CONFIG"))
app = create_app(os.getenv("FLASK_CONFIG") or "default")

with app.app_context():
    print("inserting roles ...")
    Role.insert_roles()
