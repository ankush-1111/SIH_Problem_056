import os
import sys
from pathlib import Path

# Resolve path to 'index-engine/src' relative to this script's directory
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR / "index-engine" / "src"))

from index_engine.repository import Repository
from index_engine.strategies.laspeyres import LaspeyresStrategy

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL must be set in environment")
repo = Repository(db_url)
strategy = LaspeyresStrategy()
routes = repo.fetch_route_weights()
base_periods = repo.fetch_base_period()

for dt in ['2026-09-01', '2026-10-26', '2026-10-27']:
    fares = repo.fetch_representative_fares(dt)
    windows = sorted(list(set(f.booking_window for f in fares)))
    apix = strategy.calculate(fares, routes, base_periods)
    print(f"Date {dt}: Observed Windows={windows}, Fares Count={len(fares)}, Calculated APIx={apix:.4f}")

