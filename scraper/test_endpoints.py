import requests

base = 'http://localhost:8001/api/v1/fares'

print('1. Testing /benchmark:')
r = requests.get(f'{base}/benchmark').json()
print('Sample size:', r['sample_size'], 'Corr:', r['corr'], 'MAE:', r['mae'], 'RMSE:', r['rmse'])
print('First row:', r['data'][0], 'Last row:', r['data'][-1])

print('\n2. Testing /index-contributors:')
r = requests.get(f'{base}/index-contributors').json()
print('Date:', r['date'], 'Prev Date:', r['previous_date'])
print('Current APIx:', r['current_index'], 'Prev APIx:', r['previous_index'], 'Actual Delta:', r['total_change'])
print('Change Attribution (Movement from prev period):')
for c in r['change_attribution']:
    print(' ', c['route'], f"Weight={c['weight']}", f"DeltaFare={c['current_fare'] - c['previous_fare']:+.2f}", f"Contrib={c['contribution']:+.2f} pts")
print('Sanity check:', r['sanity_check'])
print('Level Composition (Points vs Base 100):')
for l in r['level_composition']:
    print(' ', l['route'], f"Rel={l['price_relative']}", f"Contrib={l['contribution']:+.2f} pts")

print('\n3. Testing /data-quality:')
r = requests.get(f'{base}/data-quality').json()
print('Raw:', r['raw_observations'], 'Duplicates:', r['duplicates_removed'], 'Outliers:', r['outliers_filtered'], 'Clean:', r['clean_observations'], 'Retention Rate:', f"{r['retention_rate']}%")
print('Coverage:', r['total_routes'], 'routes,', r['total_airlines'], 'airlines,', r['booking_windows_count'], 'windows:', r['booking_windows'])
print('Last Run:', r['last_simulated_pipeline_run'])

print('\n4. Testing /airline-comparison:')
r = requests.get(f'{base}/airline-comparison').json()
for a in r:
    print(' ', a['airline'], f"Fare={a['representative_fare']}", a['carrier_category'])
