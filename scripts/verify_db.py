import sqlite3

def check_db():
    conn = sqlite3.connect("scraper/test_pipeline.db")
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    print(f"Tables found: {tables}")

    for table_name in tables:
        name = table_name[0]
        cur.execute(f"SELECT count(*) FROM {name}")
        print(f"Table {name} count: {cur.fetchone()[0]}")

    conn.close()

check_db()
