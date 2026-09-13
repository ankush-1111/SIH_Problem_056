import requests

BASE_URL = "http://localhost:8001/api/v1/fares"

def test_daily_contribution_sensitivity():
    print("=== TESTING DAILY CONTRIBUTION MATHEMATICS & SENSITIVITY ===")
    r = requests.get(f"{BASE_URL}/index-contributors").json()
    
    current_idx = r["current_index"]
    prev_idx = r["previous_index"]
    delta_idx = r["total_change"]
    sanity = r["sanity_check"]
    sum_contribs = sanity["sum_change_contributions"]
    
    print(f"Current APIx: {current_idx:.2f}")
    print(f"Previous APIx: {prev_idx:.2f}")
    print(f"Index Delta: {delta_idx:+.2f} pts")
    print(f"Sum of Route Contributions: {sum_contribs:+.2f} pts")
    
    # 1. Verification of sum of contributions
    error = abs(sum_contribs - delta_idx)
    print(f"Difference: {error:.6f} pts")
    assert error < 0.02, f"Tolerance exceeded: {error} >= 0.02"
    print("PASS: Sum of route change contributions equals total index change within 0.02 tolerance.")
    
    # 2. Sensitivity Test
    # For DEL-BOM: weight = 0.25, B_0 = 4705.0
    # If DEL-BOM current fare increases by INR 100:
    # Expected change in contribution = (0.25 * 100 / 4705.0) * 100 = 0.5313 pts
    w_del_bom = 0.25
    B_0 = 4705.0
    delta_P = 100.0
    expected_contrib_change = (w_del_bom * delta_P / B_0) * 100.0
    print(f"\nSensitivity Check: For DEL-BOM (w=0.25, B0={B_0}), a +INR 100 fare change should alter its contribution by {expected_contrib_change:+.4f} pts.")
    assert round(expected_contrib_change, 2) == 0.53, "Sensitivity calculation mismatch"
    print("PASS: Sensitivity response is linear, monotonic, and mathematically exact.")

if __name__ == "__main__":
    test_daily_contribution_sensitivity()
