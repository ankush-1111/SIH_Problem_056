"""Application entry point for the scraper layer.

Modes:
  python main.py --once   -> run today's five advance windows once
  python main.py --daily  -> run immediately, then every day at 08:00
"""

import argparse
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from uuid import uuid4

from config.sources import SOURCES
from scheduler.job_generator import generate_todays_jobs, ScrapeJob
from sources.mock_api_source import MockAirlineAAdapter
from sources.example_scrape_source import AirlineBAdapter
from core.retry import BlockedError, PermanentSourceError
from core.validation import is_sane_fare
from core.logger import get_logger
from db.database import engine, Base, SessionLocal
from db.models import save_fare_quote, record_job_audit

logger = get_logger("main")

ADAPTERS = {
    "airline_a": MockAirlineAAdapter(
        base_url=SOURCES["airline_a"].base_url,
        requests_per_minute=SOURCES["airline_a"].requests_per_minute,
    ),
    "airline_b": AirlineBAdapter(
        base_url=SOURCES["airline_b"].base_url,
        requests_per_minute=SOURCES["airline_b"].requests_per_minute,
    ),
}


def run_job(job: ScrapeJob, run_id: str) -> str:
    started_at = datetime.now(timezone.utc)
    adapter = ADAPTERS.get(job.source_name)
    if adapter is None:
        logger.warning(f"No adapter registered for '{job.source_name}', skipping")
        return "skipped"

    session = SessionLocal()
    status = "failed"
    error_message = None
    try:
        quote = adapter.collect(job.origin, job.destination, job.travel_date, job.advance_days)
        if not is_sane_fare(quote):
            status = "rejected"
            return status
        inserted = save_fare_quote(session, quote)
        status = "saved" if inserted else "duplicate"
        return status
    except BlockedError as exc:
        status = "blocked"
        error_message = str(exc)
        return status
    except PermanentSourceError as exc:
        status = "disabled"
        error_message = str(exc)
        return status
    except Exception as exc:
        error_message = str(exc)
        logger.error(
            f"Job failed for {job.source_name} {job.origin}->{job.destination}: {exc}"
        )
        return status
    finally:
        record_job_audit(
            session,
            run_id=run_id,
            source=job.source_name,
            origin=job.origin,
            destination=job.destination,
            travel_date=job.travel_date,
            advance_days=job.advance_days,
            started_at=started_at,
            status=status,
            finished_at=datetime.now(timezone.utc),
            error_message=error_message,
        )
        session.close()


def run_all_todays_jobs() -> None:
    run_id = str(uuid4())
    jobs = generate_todays_jobs()
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    logger.info(f"Run {run_id}: generated {len(jobs)} job(s) for {today}")

    counts: dict[str, int] = {}
    for job in jobs:
        status = run_job(job, run_id)
        counts[status] = counts.get(status, 0) + 1

    logger.info(f"Run {run_id} complete: {counts}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run today's jobs once and exit")
    parser.add_argument("--daily", action="store_true", help="Run immediately and then every day at 08:00")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)

    if args.daily:
        from apscheduler.schedulers.blocking import BlockingScheduler

        run_all_todays_jobs()
        scheduler = BlockingScheduler(timezone="Asia/Kolkata")
        scheduler.add_job(run_all_todays_jobs, "cron", hour=8, minute=0, id="daily-fare-run", replace_existing=True)
        logger.info("Scheduler started — daily at 08:00 Asia/Kolkata")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped.")
    else:
        run_all_todays_jobs()


if __name__ == "__main__":
    main()
