import psycopg2
import os

import psycopg2
import os

try:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL must be set")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Check tables
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cur.fetchall()
    print(f"Tables found: {tables}")
    
    # Check row counts in tables found
    for table in tables:
        t_name = table[0]
        cur.execute(f"SELECT COUNT(*) FROM {t_name}")
        count = cur.fetchone()[0]
        print(f"Table '{t_name}' has {count} rows.")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error connecting to DB: {e}")

