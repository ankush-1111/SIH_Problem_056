import psycopg2
import os

try:
    conn = psycopg2.connect(
        dbname="sih_db",
        user="admin",
        password="password123",
        host="localhost",
        port="5432"
    )
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

