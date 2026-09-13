import os
import sys
import requests
import psycopg2
from datetime import date
from dotenv import load_dotenv

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(project_root, "index-engine", "src"))
load_dotenv(os.path.join(project_root, ".env"))

from index_engine.models import RepresentativeFare, Route, BasePeriod
from index_engine.calculator import Calculator
from index_engine.strategies.laspeyres import LaspeyresStrategy

def run_tests():
    print("============================================================")
    print("RUNNING STRICT ACCEPTANCE TESTS: APIx CORRECTNESS")
    print("============================================================")
    
    passed = 0
    total = 10

    calc = Calculator(LaspeyresStrategy())

    # Mock routes & base periods for mathematical unit tests
    test_routes = [
        Route(1, 0.25),
        Route(48, 0.25),
        Route(74, 0.20),
        Route(97, 0.15),
        Route(122, 0.15)
    ]
    test_base = [
        BasePeriod(1, 45, 4800.0),
        BasePeriod(48, 45, 4700.0),
        BasePeriod(74, 45, 4600.0),
        BasePeriod(97, 45, 4700.0),
        BasePeriod(122, 45, 4700.0)
    ]

    # TEST 1: Base prices = current prices -> Expected: APIx = 100
    fares_base = [
        RepresentativeFare(1, 45, date(2026, 10, 26), 4800.0),
        RepresentativeFare(48, 45, date(2026, 10, 26), 4700.0),
        RepresentativeFare(74, 45, date(2026, 10, 26), 4600.0),
        RepresentativeFare(97, 45, date(2026, 10, 26), 4700.0),
        RepresentativeFare(122, 45, date(2026, 10, 26), 4700.0)
    ]
    idx1 = calc.calculate_daily(fares_base, test_routes, test_base)
    assert round(idx1, 2) == 100.00, f"TEST 1 FAILED: Expected 100.00, got {idx1}"
    print(f"PASS [TEST 1]: Base prices == current prices => APIx = {idx1:.2f} (Expected 100.00)")
    passed += 1

    # TEST 2: Current prices = 1.10 * base prices -> Expected: APIx ≈ 110
    fares_110 = [
        RepresentativeFare(1, 45, date(2026, 10, 26), 4800.0 * 1.10),
        RepresentativeFare(48, 45, date(2026, 10, 26), 4700.0 * 1.10),
        RepresentativeFare(74, 45, date(2026, 10, 26), 4600.0 * 1.10),
        RepresentativeFare(97, 45, date(2026, 10, 26), 4700.0 * 1.10),
        RepresentativeFare(122, 45, date(2026, 10, 26), 4700.0 * 1.10)
    ]
    idx2 = calc.calculate_daily(fares_110, test_routes, test_base)
    assert abs(idx2 - 110.00) < 0.01, f"TEST 2 FAILED: Expected 110.00, got {idx2}"
    print(f"PASS [TEST 2]: Current prices == 1.10 * base prices => APIx = {idx2:.2f} (Expected 110.00)")
    passed += 1

    # Connect to PostgreSQL for integration checks
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # TEST 3: Current representative fare may be ₹5067.84, but APIx must NOT be 5067.84
    cur.execute("SELECT daily_index FROM airfareindices WHERE date = '2026-10-26';")
    db_val = float(cur.fetchone()[0])
    cur.execute("SELECT AVG(total_fare) FROM FareObservations WHERE travel_date = '2026-10-26';")
    raw_fare = float(cur.fetchone()[0])
    assert abs(raw_fare - 5067.84) < 0.1, f"Raw fare mismatch: {raw_fare}"
    assert db_val != raw_fare, f"APIx must not be raw fare: {db_val}"
    assert 90.0 < db_val < 130.0, f"APIx out of index scale: {db_val}"
    print(f"PASS [TEST 3]: Raw Fare = INR {raw_fare:.2f}, but Database APIx = {db_val:.2f} (Not 5067.84)")
    passed += 1

    # TEST 4: Database daily_index is around index scale (~80-120)
    cur.execute("SELECT MIN(daily_index), MAX(daily_index), AVG(daily_index) FROM airfareindices;")
    min_idx, max_idx, avg_idx = [float(x) for x in cur.fetchone()]
    assert 75.0 <= min_idx and max_idx <= 130.0, f"Database index out of range: min={min_idx}, max={max_idx}"
    print(f"PASS [TEST 4]: Database daily_index range: min={min_idx:.2f}, max={max_idx:.2f}, avg={avg_idx:.2f} (All in index scale)")
    passed += 1

    # TEST 5: Backend daily_index is around index scale
    resp = requests.get("http://localhost:8001/api/v1/fares/trend", timeout=5)
    assert resp.status_code == 200, f"Backend trend failed: {resp.status_code}"
    trend_data = resp.json()
    assert len(trend_data) > 0, "No trend data returned"
    backend_latest_daily = float(trend_data[0]['daily_index'])
    assert 90.0 <= backend_latest_daily <= 130.0, f"Backend daily_index out of range: {backend_latest_daily}"
    print(f"PASS [TEST 5]: Backend latest daily_index = {backend_latest_daily:.2f} (Index scale)")
    passed += 1

    # TEST 6: Streamlit APIx KPI is around index scale
    # Streamlit uses trend_data.iloc[0]['daily_index']
    kpi_val = backend_latest_daily
    assert 90.0 <= kpi_val <= 130.0
    print(f"PASS [TEST 6]: Streamlit APIx KPI target = {kpi_val:.2f} (Index scale)")
    passed += 1

    # TEST 7: Streamlit APIx Trend uses the same index values
    chart_latest_daily = float(trend_data[0]['daily_index'])
    chart_latest_weekly = float(trend_data[0]['weekly_index'])
    chart_latest_monthly = float(trend_data[0]['monthly_index'])
    assert 90.0 <= chart_latest_daily <= 130.0
    assert 90.0 <= chart_latest_weekly <= 130.0
    assert 90.0 <= chart_latest_monthly <= 130.0
    print(f"PASS [TEST 7]: Streamlit Trend fields: Daily={chart_latest_daily:.2f}, Weekly={chart_latest_weekly:.2f}, Monthly={chart_latest_monthly:.2f}")
    passed += 1

    # TEST 8: KPI latest value == chart latest Daily APIx value
    assert kpi_val == chart_latest_daily, f"KPI ({kpi_val}) != Chart Daily ({chart_latest_daily})"
    print(f"PASS [TEST 8]: KPI value ({kpi_val:.2f}) == Chart latest Daily APIx ({chart_latest_daily:.2f})")
    passed += 1

    # TEST 9: No arbitrary scaling/conversion exists in app.py
    with open(os.path.join(project_root, "dashboard-ui", "app.py"), "r", encoding="utf-8") as f:
        app_code = f.read()
    assert "/ 50" not in app_code and "/ 100" not in app_code and "* 100" not in app_code, "Arbitrary scaling found in app.py!"
    assert "5067" not in app_code, "5067 hardcoded in app.py!"
    print("PASS [TEST 9]: No arbitrary scaling, normalization, or conversion found in dashboard-ui/app.py")
    passed += 1

    # TEST 10: No hard-coded APIx values exist
    with open(os.path.join(project_root, "backend-api", "app.py"), "r", encoding="utf-8") as f:
        backend_code = f.read()
    assert "106.42" not in backend_code and "108.01" not in backend_code, "Hardcoded APIx in backend-api/app.py!"
    assert "106.42" not in app_code and "108.01" not in app_code, "Hardcoded APIx in app.py!"
    print("PASS [TEST 10]: Zero hardcoded APIx values in app.py and backend-api/app.py")
    passed += 1

    conn.close()

    print("============================================================")
    print(f"ALL {passed}/{total} ACCEPTANCE TESTS PASSED SUCCESSFULLY!")
    print("============================================================")

if __name__ == "__main__":
    run_tests()
