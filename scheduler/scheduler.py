from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from pytz import timezone
from scheduler.config import TEST_MODE, TEST_INTERVAL_SECONDS, PRODUCTION_HOUR, PRODUCTION_MINUTE, TIMEZONE, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from scheduler.logger import logger
from scheduler.jobs import test_job, run_scraper_job, run_representative_fare_aggregation_job

def start_scheduler():
    logger.info("Initializing scheduler...")

    tz = timezone(TIMEZONE)

    # Configure job store
    jobstores = {
        'default': SQLAlchemyJobStore(url=f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    }

    scheduler = BlockingScheduler(jobstores=jobstores, timezone=tz)

    if TEST_MODE:
        logger.info(f"Running in TEST_MODE with interval: {TEST_INTERVAL_SECONDS} seconds")
        scheduler.add_job(test_job, 'interval', seconds=TEST_INTERVAL_SECONDS, id='test_job', max_instances=1)
        scheduler.add_job(run_representative_fare_aggregation_job, 'interval', seconds=TEST_INTERVAL_SECONDS * 2, id='fare_aggregation_job', max_instances=1)
    else:
        logger.info(f"Running in PRODUCTION_MODE daily at {PRODUCTION_HOUR}:{PRODUCTION_MINUTE}")
        scheduler.add_job(run_scraper_job, 'cron', hour=PRODUCTION_HOUR, minute=PRODUCTION_MINUTE, id='scraper_job', max_instances=1)
        scheduler.add_job(run_representative_fare_aggregation_job, 'cron', hour=PRODUCTION_HOUR, minute=(PRODUCTION_MINUTE + 30) % 60, id='fare_aggregation_job', max_instances=1)

    logger.info("Scheduler started successfully.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutting down.")

if __name__ == "__main__":
    start_scheduler()
