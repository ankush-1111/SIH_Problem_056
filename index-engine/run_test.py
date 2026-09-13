
import os
from index_engine.service import IndexService
from index_engine.repository import Repository
from index_engine.calculator import Calculator
from index_engine.strategies.laspeyres import LaspeyresStrategy
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password123@localhost:5432/sih_db")

repo = Repository(DATABASE_URL)
strategy = LaspeyresStrategy()
calc = Calculator(strategy)
service = IndexService(repo, calc)

# Run full pipeline for target date
target_date = "2026-10-26"
try:
    results = service.run_full_pipeline(target_date)
    print(f"Pipeline results for {target_date}: {results}")
except Exception as e:
    print(f"Pipeline failed: {e}")
    import traceback
    traceback.print_exc()

