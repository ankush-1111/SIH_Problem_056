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
