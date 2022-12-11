import os
import sys

import psycopg2
import requests

basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, f"{basedir}/../")
from app import create_app
from app.dbmodels import User

streaming_user = os.getenv("STREAMING_USER")
streaming_password = os.getenv("STREAMING_PASSWORD")
workflow_user = os.getenv("WORKFLOW_USER")
workflow_password = os.getenv("WORKFLOW_PASSWORD")


users = [
    (
        streaming_user.strip(),
        streaming_password.strip(),
        "streaming",
        "streaming account",
    ),
    (workflow_user.strip(), workflow_password.strip(), "workflow", "workflow account"),
    ("falcoeye-test@falcoeye.io", "falcoeye-test", "falcoeye-test", "test account"),
]

print(os.getenv("FLASK_CONFIG"))
app = create_app(os.getenv("FLASK_CONFIG") or "default")

with app.app_context():

    for user in users:
        print(f"registering service users... { user[0]}")
        payload = {
            "email": user[0],
            "password": user[1],
            "username": user[2],
            "name": user[3],
        }
        User.register_as_service_account(payload)


# URL = "http://localhost:5000"

# db_url = os.getenv("DATABASE_URL")
# with psycopg2.connect(db_url) as conn:

# r = requests.post(f"{URL}/auth/register", json=payload)


# with conn.cursor() as curs:
#     curs.execute("select id from public.roles where name='Admin'")
#     role_id = curs.fetchone()[0]
#     curs.execute(
#         "UPDATE public.user SET role_id = %s WHERE email = %s",
#         (role_id, user[0]),
#     )
# conn.commit()
