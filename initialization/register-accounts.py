import os

import psycopg2
import requests

URL = "http://localhost:5000"

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
]


db_url = os.getenv("DATABASE_URL")
with psycopg2.connect(db_url) as conn:
    for user in users:
        payload = {
            "email": user[0],
            "password": user[1],
            "username": user[2],
            "name": user[3],
        }
        r = requests.post(f"{URL}/auth/register", json=payload)
        with conn.cursor() as curs:
            curs.execute("select id from public.roles where name='Admin'")
            role_id = curs.fetchone()[0]
            curs.execute(
                "UPDATE public.user SET role_id = %s WHERE email = %s",
                (role_id, user[0]),
            )
        conn.commit()
