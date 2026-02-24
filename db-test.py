import psycopg2

conn = psycopg2.connect(
    dbname="finance_app",
    user="ritikmahajan",
    password="",   # usually empty locally
    host="localhost",
    port="5432"
)

cur = conn.cursor()


cur.execute("SELECT 1;")

cur.close()
conn.close()
