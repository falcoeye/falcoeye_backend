import os
import uuid

import psycopg2
import requests

URL = "http://localhost:5000"

streaming_user = os.getenv("STREAMING_USER")
streaming_password = os.getenv("STREAMING_PASSWORD")

if streaming_user:
    streaming_user = streaming_user.strip()

if streaming_password:
    streaming_password = streaming_password.strip()

streaming_info = {
    "email": streaming_user.strip(),
    "username": "streaming",
    "name": "streaming microservice",
    "password": streaming_password,
}

r = requests.post(f"{URL}/auth/register", json=streaming_info)
db_url = os.getenv("DATABASE_URL")
with psycopg2.connect(db_url) as conn:
    with conn.cursor() as curs:
        curs.execute("select id from public.roles where name='Admin'")
        role_id = curs.fetchone()[0]
    with conn.cursor() as curs:
        curs.execute(
            "UPDATE public.user SET role_id = %s WHERE email = %s",
            (role_id, streaming_user),
        )
    conn.commit()
