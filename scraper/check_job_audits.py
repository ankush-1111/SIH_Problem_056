import psycopg2

conn = psycopg2.connect('postgresql://admin:password123@localhost:5432/sih_db')
cur = conn.cursor()
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'job_audits'")
print('job_audits schema:', cur.fetchall())
cur.execute("SELECT status, COUNT(*) FROM job_audits GROUP BY status")
print('job_audits by status:', cur.fetchall())

cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'fare_observations'")
print('fare_observations cols:', [c[0] for c in cur.fetchall()])
cur.execute("SELECT availability, COUNT(*) FROM fare_observations GROUP BY availability")
print('availability in fare_observations:', cur.fetchall())


