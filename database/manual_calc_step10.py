import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

target_date = '2026-10-26'

print(f"=== STEP 10 MANUAL CALCULATION FOR {target_date} ===")

# Query Route, Weight, Base Fare, Current Fare for active routes on 2026-10-26
cur.execute("""
    SELECT r.origin || '-' || r.destination as route_name,
           r.weight,
           bp.booking_window,
           bp.base_fare,
           rf.median_fare as current_fare
    FROM representativefares rf
    JOIN routes r ON rf.route_id = r.id
    JOIN baseperiods bp ON rf.route_id = bp.route_id AND rf.booking_window = bp.booking_window
    WHERE rf.date = %s AND r.weight > 0
    ORDER BY r.id;
""", (target_date,))

rows = cur.fetchall()

print(f"{'Route':<10} {'Window':<8} {'Weight':<8} {'Base Fare':<12} {'Current Fare':<14} {'Price Relative':<14}")
print("-" * 70)

weighted_current_sum = 0.0
weighted_base_sum = 0.0
weighted_relative_sum = 0.0
total_weight = 0.0

for r in rows:
    route_name, weight, window, base_fare, current_fare = r
    weight = float(weight)
    base_fare = float(base_fare)
    current_fare = float(current_fare)
    relative = (current_fare / base_fare) * 100.0

    weighted_current_sum += current_fare * weight
    weighted_base_sum += base_fare * weight
    weighted_relative_sum += relative * weight
    total_weight += weight

    print(f"{route_name:<10} T+{window:<6} {weight:<8.4f} INR {base_fare:<10.2f} INR {current_fare:<10.2f} {relative:<14.2f}")

print("-" * 70)
print(f"Total Weight: {total_weight:.4f}")
print(f"Weighted Current Fare Sum = SUM(Weight * Current Fare) = INR {weighted_current_sum:.4f}")
print(f"Weighted Base Fare Sum    = SUM(Weight * Base Fare)    = INR {weighted_base_sum:.4f}")

laspeyres_apix = (weighted_current_sum / weighted_base_sum) * 100.0
print(f"\nFinal APIx (Laspeyres Price Index) = (Weighted Current Sum / Weighted Base Sum) * 100")
print(f"                                   = ({weighted_current_sum:.4f} / {weighted_base_sum:.4f}) * 100")
print(f"                                   = {laspeyres_apix:.2f}")

cur.execute("SELECT daily_index FROM airfareindices WHERE date = %s", (target_date,))
stored_idx = cur.fetchone()[0]
print(f"Stored daily_index in airfareindices for {target_date}: {stored_idx}")
assert abs(float(stored_idx) - round(laspeyres_apix, 2)) < 0.01, f"Mismatch: stored {stored_idx} vs calculated {laspeyres_apix}"
print("=> MANUAL CALCULATION AND STORED VALUE MATCH PERFECTLY!")

conn.close()
