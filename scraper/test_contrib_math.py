import psycopg2
from collections import defaultdict

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL must be set in environment")
conn = psycopg2.connect(db_url)
cur = conn.cursor()

# Get routes and weights
cur.execute("SELECT id, origin || '-' || destination, weight FROM routes WHERE weight > 0")
routes = {row[0]: {'name': row[1], 'weight': float(row[2])} for row in cur.fetchall()}

# Get base fares
cur.execute('SELECT route_id, booking_window, base_fare FROM baseperiods')
base_fares = {(row[0], row[1]): float(row[2]) for row in cur.fetchall()}

def get_route_fares_and_base(dt):
    cur.execute('SELECT route_id, booking_window, median_fare FROM representativefares WHERE date = %s', (dt,))
    rows = cur.fetchall()
    cur_by_route = defaultdict(list)
    base_by_route = defaultdict(list)
    for r_id, bw, fare in rows:
        if r_id in routes and (r_id, bw) in base_fares:
            cur_by_route[r_id].append(float(fare))
            base_by_route[r_id].append(base_fares[(r_id, bw)])
    
    route_avg_cur = {}
    route_avg_base = {}
    for r_id in routes:
        if r_id in cur_by_route:
            route_avg_cur[r_id] = sum(cur_by_route[r_id]) / len(cur_by_route[r_id])
            route_avg_base[r_id] = sum(base_by_route[r_id]) / len(base_by_route[r_id])
    return route_avg_cur, route_avg_base

cur27, base27 = get_route_fares_and_base('2026-10-27')
cur26, base26 = get_route_fares_and_base('2026-10-26')

B0 = sum(routes[r_id]['weight'] * base27[r_id] for r_id in routes)
print('Weighted Base Fare B0:', B0)

current_weighted_sum = sum(routes[r_id]['weight'] * cur27[r_id] for r_id in routes)
prev_weighted_sum = sum(routes[r_id]['weight'] * cur26[r_id] for r_id in routes)

apix27 = (current_weighted_sum / B0) * 100
apix26 = (prev_weighted_sum / B0) * 100

print(f'APIx 2026-10-27: {apix27:.4f}')
print(f'APIx 2026-10-26: {apix26:.4f}')
print(f'Delta APIx: {apix27 - apix26:.4f}')

print('\nRoute Change Contributions:')
sum_contrib = 0.0
for r_id, r_info in sorted(routes.items(), key=lambda x: x[1]['weight'], reverse=True):
    w = r_info['weight']
    p_t = cur27.get(r_id, 0)
    p_prev = cur26.get(r_id, 0)
    # Contribution to change: w * (p_t - p_prev) / B0 * 100
    contrib = (w * (p_t - p_prev) / B0) * 100
    sum_contrib += contrib
    pct_route_change = ((p_t - p_prev) / p_prev) * 100 if p_prev else 0
    print(f"{r_info['name']}: Weight={w:.2f}, Cur={p_t:.2f}, Prev={p_prev:.2f}, RouteChange={pct_route_change:+.2f}%, Contrib={contrib:+.4f} pts")

print(f'Sum of Contributions: {sum_contrib:+.4f} pts')
print(f'Difference from Delta APIx: {sum_contrib - (apix27 - apix26):.6f}')

print('\nRoute Level Composition (Why APIx is at 107.58 vs Base 100):')
sum_level = 0.0
for r_id, r_info in sorted(routes.items(), key=lambda x: x[1]['weight'], reverse=True):
    w = r_info['weight']
    p_t = cur27.get(r_id, 0)
    p_base = base27.get(r_id, 0)
    contrib_level = (w * (p_t - p_base) / B0) * 100
    sum_level += contrib_level
    print(f"{r_info['name']}: Weight={w:.2f}, Cur={p_t:.2f}, Base={p_base:.2f}, LevelContrib={contrib_level:+.4f} pts")

print(f'Sum of Level Contribs: {sum_level:+.4f} pts')
print(f'APIx - 100: {apix27 - 100:+.4f} pts')
print(f'Difference from (APIx - 100): {sum_level - (apix27 - 100):.6f}')

