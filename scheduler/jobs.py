import subprocess
from scheduler.logger import logger

def test_job():
    logger.info("Scheduler test job executed successfully.")

def run_scraper_job():
    try:
        logger.info("Starting Airfare scraping job...")
        # TODO: Call scraper entry point
        logger.info("Airfare scraping completed.")
    except Exception as e:
        logger.error(f"Airfare scraping job failed: {e}")

def run_representative_fare_aggregation_job():
    try:
        logger.info("Starting Representative Fare aggregation job...")
        subprocess.run(["python", "../representative-fare-engine/service.py"], check=True)
        logger.info("Representative Fare aggregation completed.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Representative Fare aggregation job failed: {e}")
