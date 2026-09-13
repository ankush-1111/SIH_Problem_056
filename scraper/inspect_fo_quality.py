import psycopg2

conn = psycopg2.connect('postgresql://admin:password123@localhost:5432/sih_db')
cur = conn.cursor()

# Check total rows in FareObservations
cur.execute('SELECT COUNT(*) FROM FareObservations')
total_fo = cur.fetchone()[0]
print('Total rows in FareObservations:', total_fo)

# Check nulls or <= 0
cur.execute('SELECT COUNT(*) FROM FareObservations WHERE total_fare IS NULL OR total_fare <= 0')
invalid_fares = cur.fetchone()[0]
print('Invalid or <= 0 fares:', invalid_fares)

# Check duplicate observations (same route_id, airline_id, search_date, travel_date, booking_window)
cur.execute('''
    SELECT route_id, airline_id, search_date, travel_date, booking_window, COUNT(*) 
    FROM FareObservations 
    GROUP BY route_id, airline_id, search_date, travel_date, booking_window 
    HAVING COUNT(*) > 1
''')
dup_groups = cur.fetchall()
print('Number of duplicate groups:', len(dup_groups))

# Total duplicate rows count
cur.execute('''
    SELECT SUM(cnt - 1) FROM (
        SELECT COUNT(*) as cnt 
        FROM FareObservations 
        GROUP BY route_id, airline_id, search_date, travel_date, booking_window 
        HAVING COUNT(*) > 1
    ) sub
''')
dup_rows = cur.fetchone()[0] or 0
print('Total redundant/duplicate observations:', dup_rows)

# Outlier check: total_fare < 1500 or total_fare > 30000 (standard Indian domestic bounds)
cur.execute('SELECT COUNT(*) FROM FareObservations WHERE total_fare < 1500 OR total_fare > 30000')
outlier_count = cur.fetchone()[0]
print('Outliers (<1500 or >30000):', outlier_count)

# Missing values in crucial fields
cur.execute('SELECT COUNT(*) FROM FareObservations WHERE total_fare IS NULL OR base_fare IS NULL OR route_id IS NULL OR booking_window IS NULL')
missing_count = cur.fetchone()[0]
print('Missing critical fields:', missing_count)

# Date range in FareObservations
cur.execute('SELECT MIN(search_date), MAX(search_date) FROM FareObservations')
print('Search date range in FareObservations:', cur.fetchall())
cur.execute('SELECT MIN(travel_date), MAX(travel_date) FROM FareObservations')
print('Travel date range in FareObservations:', cur.fetchall())


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
