import os

import psycopg2

db_url = os.getenv("DATABASE_URL")
with psycopg2.connect(db_url) as conn:
    with conn.cursor() as curs:
        curs.execute("delete from public.analysis")

import os

import psycopg2

db_url = os.getenv("DATABASE_URL")
with psycopg2.connect(db_url) as conn:
    with conn.cursor() as curs:
        curs.execute("select * from public.user")
        while user := curs.fetchone():
            print(user)
