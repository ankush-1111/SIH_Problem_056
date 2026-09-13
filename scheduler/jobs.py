import subprocess
from tenacity import retry, stop_after_attempt, wait_exponential
from scheduler.logger import logger

def test_job():
    logger.info("Scheduler test job executed successfully.")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def run_scraper_job():
    try:
        logger.info("Starting Airfare scraping job...")
        subprocess.run(["python", "main.py", "--once"], check=True, cwd="../scraper/")
        logger.info("Airfare scraping completed.")
    except Exception as e:
        logger.error(f"Airfare scraping job failed: {e}")
        raise

def run_representative_fare_aggregation_job():
    try:
        logger.info("Starting Representative Fare aggregation job...")
        subprocess.run(["python", "../representative-fare-engine/service.py"], check=True)
        logger.info("Representative Fare aggregation completed.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Representative Fare aggregation job failed: {e}")
        raise

def run_index_engine_job():
    try:
        logger.info("Starting Index Engine pipeline...")
        subprocess.run(["python", "run_test.py"], check=True, cwd="../index-engine/")
        logger.info("Index Engine pipeline completed.")
    except Exception as e:
        logger.error(f"Index Engine job failed: {e}")
        raise
