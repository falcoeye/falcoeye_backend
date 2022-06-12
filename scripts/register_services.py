import os

import psycopg2
import requests

streaming_user = os.getenv("STREAMING_USER")
streaming_password = os.getenv("STREAMING_PASSWORD")

streaming_info = {
    "email": streaming_user,
    "username": "streaming",
    "name": "streaming microservice",
    "password": streaming_password,
}

r = requests.post("http://localhost:5000", json=streaming_info)

db_url = os.getenv("DATABASE_URL")
with psycopg2.connect(db_url) as conn:
    with conn.cursor() as curs:
        curs.execute("select id from roles where name=%(name)s", {"name": "Admin"})
        role_id = curs.fetchone()[0]
        curs.execute(
            "update user set role_id=%(role_id)s where email=%(email)s",
            {"role_id": role_id, "email": streaming_user},
        )
        conn.commit()
