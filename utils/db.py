from psycopg2 import pool
from psycopg2.pool import PoolError
from contextlib import contextmanager

import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER= os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

if(not DB_PORT or not DB_HOST or not DB_NAME or not DB_USER ):
    raise RuntimeError("ENV not set")

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
)

@contextmanager
def get_connection():
    try:
        conn = connection_pool.getconn()
    except PoolError:
        from exceptions import DbPoolExhaustedError
        raise DbPoolExhaustedError()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        connection_pool.putconn(conn)
