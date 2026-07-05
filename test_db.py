import psycopg2
from config import DATABASE

try:
    conn = psycopg2.connect(DATABASE)

    print("Kết nối thành công!")

    cur = conn.cursor()

    cur.execute("SELECT version();")

    print(cur.fetchone())

    conn.close()

except Exception as e:
    print(e)