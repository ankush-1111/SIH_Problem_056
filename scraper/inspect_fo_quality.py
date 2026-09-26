import psycopg2
import os

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL must be set in environment")
conn = psycopg2.connect(db_url)
cur = conn.cursor()

# Check total rows in fare_observations
cur.execute('SELECT COUNT(*) FROM fare_observations')
total_fo = cur.fetchone()[0]
print('Total rows in fare_observations:', total_fo)

# Check nulls or <= 0
cur.execute('SELECT COUNT(*) FROM fare_observations WHERE total_fare IS NULL OR total_fare <= 0')
invalid_fares = cur.fetchone()[0]
print('Invalid or <= 0 fares:', invalid_fares)

# Check duplicate observations (same source, origin, destination, travel_date, advance_days)
cur.execute('''
    SELECT source, origin, destination, travel_date, advance_days, COUNT(*)
    FROM fare_observations
    GROUP BY source, origin, destination, travel_date, advance_days
    HAVING COUNT(*) > 1
''')
dup_groups = cur.fetchall()
print('Number of duplicate groups:', len(dup_groups))

# Total duplicate rows count
cur.execute('''
    SELECT SUM(cnt - 1) FROM (
        SELECT COUNT(*) as cnt
        FROM fare_observations
        GROUP BY source, origin, destination, travel_date, advance_days
        HAVING COUNT(*) > 1
    ) sub
''')
dup_rows = cur.fetchone()[0] or 0
print('Total redundant/duplicate observations:', dup_rows)

# Outlier check: total_fare < 1500 or total_fare > 30000 (standard Indian domestic bounds)
cur.execute('SELECT COUNT(*) FROM fare_observations WHERE total_fare < 1500 OR total_fare > 30000')
outlier_count = cur.fetchone()[0]
print('Outliers (<1500 or >30000):', outlier_count)

# Missing values in crucial fields
cur.execute('SELECT COUNT(*) FROM fare_observations WHERE total_fare IS NULL OR base_fare IS NULL OR travel_date IS NULL OR origin IS NULL OR destination IS NULL')
missing_count = cur.fetchone()[0]
print('Missing critical fields:', missing_count)

# Date range in fare_observations
cur.execute('SELECT MIN(observation_timestamp), MAX(observation_timestamp) FROM fare_observations')
print('Observation timestamp range in fare_observations:', cur.fetchall())
cur.execute('SELECT MIN(travel_date), MAX(travel_date) FROM fare_observations')
print('Travel date range in fare_observations:', cur.fetchall())


# Check RepresentativeFares count
cur.execute('SELECT COUNT(*) FROM representativefares')
total_rf = cur.fetchone()[0]
print('Total representative fares in representativefares:', total_rf)

# Check if there are other tables like raw observations or log
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
""")
tables = [t[0] for t in cur.fetchall()]
print('Public tables in DB:', tables)
