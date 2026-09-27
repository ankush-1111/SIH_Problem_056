"""Generate the five daily advance-purchase observations."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from config.sources import get_active_sources

ADVANCE_WINDOWS = (45, 30, 15, 7, 1)
ROUTES = (
    ("DEL", "BOM"),
    ("DEL", "BLR"),
    ("BOM", "BLR"),
    ("DEL", "HYD"),
    ("BOM", "HYD"),
)


@dataclass(frozen=True)
class ScrapeJob:
    source_name: str
    origin: str
    destination: str
    travel_date: date
    advance_days: int


def generate_todays_jobs(today: date | None = None) -> list[ScrapeJob]:
    """For today, create one job per source/route/window.

    A T-45 observation today targets today + 45 days, T-30 targets
    today + 30 days, etc. This removes the old hardcoded travel dates.
    """
    today = today or datetime.now(ZoneInfo("Asia/Kolkata")).date()
    active_sources = get_active_sources()
    jobs: list[ScrapeJob] = []

    for advance_days in ADVANCE_WINDOWS:
        travel_date = today + timedelta(days=advance_days)
        for origin, destination in ROUTES:
            for source_name in active_sources:
                jobs.append(
                    ScrapeJob(
                        source_name=source_name,
                        origin=origin,
                        destination=destination,
                        travel_date=travel_date,
                        advance_days=advance_days,
                    )
                )
    return jobs
