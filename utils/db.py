from psycopg2 import pool
from contextlib import contextmanager

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname="finance_app",
    user="ritikmahajan",
    password="",
    host="localhost",
    port="5432"
)

@contextmanager
def get_connection():
    conn = connection_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        connection_pool.putconn(conn)