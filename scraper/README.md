# SIH Airfare Price Index — Scraper/Data-Collection Layer v2

This repository is the scraper/data-collection layer only. It produces normalized fare observations for the cleaning, index, backend API, and dashboard layers.

## Core pipeline

```text
SOURCE REGISTRY
   ↓
ACCESS POLICY (API first / permitted scrape only)
   ↓
API or Playwright ADAPTER
   ↓
RAW RESPONSE / PAGE EXTRACTION
   ↓
NORMALIZED FareQuote
   ↓
VALIDATION + FARE SELECTION RULE
   ↓
FARE OBSERVATION DB + JOB AUDIT LOG
```

### Non-negotiable access rule

1. Use an authorized official/partner API when available.
2. Scrape only when automated access is explicitly permitted by the source policy.
3. Never solve CAPTCHAs, evade fingerprinting, rotate proxies/IPs to bypass blocks, or otherwise defeat anti-bot controls.
4. If access is blocked or the policy is uncertain, mark the source as blocked/disabled and continue with the remaining sources.

## What changed in v2

- **Dynamic travel dates:** every run creates T-45, T-30, T-15, T-7 and T-1 observations relative to today's date. No hardcoded September/October dates.
- **More representative fare schema:** flight number, cabin, fare family, stops, departure/arrival time and a standardized search profile are available.
- **Money is stored as Decimal/Numeric(12,2):** avoids binary floating-point problems for fare values.
- **Stronger validation:** fare components must reconcile, date/advance-window consistency is checked, negative charges are rejected, and unavailable fares do not enter the observation table.
- **Explicit source metadata:** API docs, ToS/robots links, access verification date, and per-source request pacing can be recorded.
- **Safer retries:** block and permanent-access errors are not retried; ordinary failures use bounded exponential backoff.
- **Per-source rate limiting:** each source can specify its own requests-per-minute value.
- **Job audit trail:** each run gets a `run_id`; every job is logged as saved, duplicate, rejected, blocked, disabled, or failed.
- **Environment loading:** `.env` is now actually loaded.
- **PostgreSQL readiness:** the PostgreSQL driver is included while SQLite remains the zero-setup local default.
- **Tests included:** job generation, fare schema, and validation tests are now present.
- **Daily mode runs once immediately:** `--daily` no longer waits until the next morning for its first collection.

## Standardized search profile

The prototype assumes:

- one-way trip
- 1 passenger
- economy cabin
- INR pricing
- one representative fare per source/route/travel date/advance window
- representative fare = the lowest available fare satisfying the profile

Keep this profile identical across sources as much as the source allows. If a source cannot expose a comparable field, store what it provides and document the difference.

## Setup

```bash
python -m venv venv
# Windows: venv\\Scripts\\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
```

Run once:

```bash
python main.py --once
```

Run continuously:

```bash
python main.py --daily
```

### Database

Default local DB:

```text
sqlite:///./airfare_data.db
```

For PostgreSQL, set for example:

```text
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/airfare_db
```

## Source onboarding checklist

Before adding a real source:

- Confirm whether an official API/partner API exists.
- Record the API documentation URL if applicable.
- Review Terms of Service and robots/access rules for automated collection.
- Record the verification date and source-specific request limit.
- Implement only the adapter for that source.
- Test a normal response, timeout, empty result, malformed fare, 429/403, and CAPTCHA/block page.
- Never commit credentials; use `.env`.

## Current adapters

`example_api_source.py` and `example_scrape_source.py` are templates. They deliberately fail on their placeholder URLs instead of returning fake fares. Replace them only after you have a real, verified source.

## Tests

```bash
pytest -q
```

The tests currently cover dynamic window generation and core fare validation/schema behavior. Add a source-specific parser test whenever a real adapter is introduced.
