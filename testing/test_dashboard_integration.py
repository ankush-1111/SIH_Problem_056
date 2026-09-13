import os
import sys
import requests
import json

BASE_URL = "http://localhost:8001/api/v1/fares"
STREAMLIT_URL = "http://localhost:8501"

def test_integration():
    print("============================================================")
    print("TESTING STREAMLIT DASHBOARD INTEGRATION & DATA CONTRACTS")
    print("============================================================")

    # 1. Test Streamlit Web Server
    print("\n1. Testing Streamlit Web Server...")
    resp = requests.get(STREAMLIT_URL, timeout=5)
    assert resp.status_code == 200, f"Streamlit returned status {resp.status_code}"
    print("PASS: Streamlit dashboard is running and returned HTTP 200.")

    # 2. Test /trend endpoint
    print("\n2. Testing /trend Endpoint...")
    resp = requests.get(f"{BASE_URL}/trend", timeout=5)
    assert resp.status_code == 200, f"/trend returned {resp.status_code}"
    trend_data = resp.json()
    assert isinstance(trend_data, list) and len(trend_data) > 0, "No trend records"
    latest = trend_data[0]
    for key in ['date', 'daily_index', 'weekly_index', 'monthly_index']:
        assert key in latest, f"Missing key '{key}' in /trend"
    assert 80.0 <= latest['daily_index'] <= 130.0, f"daily_index out of index scale: {latest['daily_index']}"
    print(f"PASS: /trend returned {len(trend_data)} records. Latest Daily APIx = {latest['daily_index']:.2f}")

    # 3. Test /route-heatmap with index and fare metrics
    print("\n3. Testing /route-heatmap Endpoint...")
    # Metric = index
    resp_idx = requests.get(f"{BASE_URL}/route-heatmap", params={"metric": "index", "routes": "DEL-BOM,DEL-BLR", "windows": "T+7,T+15"})
    assert resp_idx.status_code == 200, f"/route-heatmap (index) returned {resp_idx.status_code}"
    heatmap_idx = resp_idx.json()
    assert len(heatmap_idx) > 0, "No heatmap index data"
    assert 80.0 <= heatmap_idx[0]['val'] <= 140.0, f"Heatmap index out of scale: {heatmap_idx[0]['val']}"
    
    # Metric = fare
    resp_fare = requests.get(f"{BASE_URL}/route-heatmap", params={"metric": "fare", "routes": "DEL-BOM,DEL-BLR", "windows": "T+7,T+15"})
    assert resp_fare.status_code == 200, f"/route-heatmap (fare) returned {resp_fare.status_code}"
    heatmap_fare = resp_fare.json()
    assert len(heatmap_fare) > 0, "No heatmap fare data"
    assert heatmap_fare[0]['val'] > 1000.0, f"Heatmap fare should be in monetary units: {heatmap_fare[0]['val']}"
    
    # Empty filters resilience
    resp_empty = requests.get(f"{BASE_URL}/route-heatmap", params={"metric": "index", "routes": "", "windows": ""})
    assert resp_empty.status_code == 200, f"/route-heatmap with empty filters failed: {resp_empty.status_code}"
    print(f"PASS: /route-heatmap handles index ({heatmap_idx[0]['val']:.1f}), fare (INR {heatmap_fare[0]['val']:,.0f}), and empty filters cleanly.")

    # 4. Test /elasticity (Lead-time fare curve)
    print("\n4. Testing /elasticity Endpoint (Lead-Time Fare Curve)...")
    resp_el = requests.get(f"{BASE_URL}/elasticity", params={"route": "DEL-BOM"})
    assert resp_el.status_code == 200, f"/elasticity returned {resp_el.status_code}"
    el_data = resp_el.json()
    assert len(el_data) > 0, "No elasticity records"
    for item in el_data:
        assert 'booking_window' in item and 'avg_fare' in item and 'label' in item
        assert item['avg_fare'] > 1000.0, "Elasticity fare must be monetary"
    print(f"PASS: /elasticity returned {len(el_data)} windows for DEL-BOM: {[d['label'] for d in el_data]}")

    # 5. Test /airline-comparison
    print("\n5. Testing /airline-comparison Endpoint...")
    resp_air = requests.get(f"{BASE_URL}/airline-comparison", params={"route": "DEL-BOM"})
    assert resp_air.status_code == 200, f"/airline-comparison returned {resp_air.status_code}"
    air_data = resp_air.json()
    assert len(air_data) > 0, "No airline comparison data"
    assert 'airline' in air_data[0] and 'representative_fare' in air_data[0]
    print(f"PASS: /airline-comparison returned {len(air_data)} airlines: {[a['airline'] for a in air_data]}")

    # 6. Test /index-contributors
    print("\n6. Testing /index-contributors Endpoint...")
    resp_contrib = requests.get(f"{BASE_URL}/index-contributors")
    assert resp_contrib.status_code == 200, f"/index-contributors returned {resp_contrib.status_code}"
    contrib_data = resp_contrib.json()
    for key in ['date', 'current_index', 'previous_index', 'change_percent', 'contributors']:
        assert key in contrib_data, f"Missing key '{key}' in /index-contributors"
    contributors = contrib_data['contributors']
    assert len(contributors) > 0, "Contributors list is empty"
    top_c = contributors[0]
    assert 'route' in top_c and 'weight' in top_c and 'price_relative' in top_c and 'contribution' in top_c
    print(f"PASS: /index-contributors: Current={contrib_data['current_index']:.2f}, Change={contrib_data['change_percent']:+.2f}%, Top Route={top_c['route']} ({top_c['contribution']:+.2f} pts)")

    # 7. Test /benchmark (DGCA Backtest)
    print("\n7. Testing /benchmark Endpoint (DGCA Backtest)...")
    resp_bench = requests.get(f"{BASE_URL}/benchmark")
    assert resp_bench.status_code == 200, f"/benchmark returned {resp_bench.status_code}"
    bench_data = resp_bench.json()
    for key in ['data', 'corr', 'mae', 'rmse']:
        assert key in bench_data, f"Missing key '{key}' in /benchmark"
    bench_rows = bench_data['data']
    assert len(bench_rows) > 0, "No benchmark comparison data"
    assert 'date' in bench_rows[0] and 'dgca_benchmark' in bench_rows[0] and 'apix' in bench_rows[0]
    print(f"PASS: /benchmark: Correlation={bench_data['corr']}, MAE={bench_data['mae']}, RMSE={bench_data['rmse']}, Rows={len(bench_rows)}")

    # 8. Test /data-quality (KeyError 'total' prevention)
    print("\n8. Testing /data-quality Endpoint...")
    resp_qual = requests.get(f"{BASE_URL}/data-quality")
    assert resp_qual.status_code == 200, f"/data-quality returned {resp_qual.status_code}"
    qual_data = resp_qual.json()
    for key in ['total', 'total_observations', 'valid', 'valid_observations', 'outliers', 'duplicates', 'coverage_pct']:
        assert key in qual_data, f"Missing required key '{key}' in /data-quality"
    assert qual_data['coverage_pct'] > 0.0, "Invalid coverage percentage"
    print(f"PASS: /data-quality: Total Obs={qual_data['total_observations']:,}, Valid={qual_data['valid_observations']:,}, Coverage={qual_data['coverage_pct']:.1f}%")

    print("\n============================================================")
    print("ALL DASHBOARD INTEGRATION AND CONTRACT TESTS PASSED!")
    print("============================================================")

if __name__ == "__main__":
    test_integration()
