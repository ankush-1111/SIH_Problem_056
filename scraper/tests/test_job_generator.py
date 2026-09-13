from datetime import date

from scheduler.job_generator import generate_todays_jobs, ADVANCE_WINDOWS, ROUTES


def test_jobs_are_dynamic_and_cover_all_windows():
    jobs = generate_todays_jobs(date(2026, 9, 5))
    assert {j.advance_days for j in jobs} == set(ADVANCE_WINDOWS)
    assert len(jobs) == len(ADVANCE_WINDOWS) * len(ROUTES) * 2
    assert all((job.travel_date - date(2026, 9, 5)).days == job.advance_days for job in jobs)
