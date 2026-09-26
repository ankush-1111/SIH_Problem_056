# Phase 3 — Scraper / Source-Ingestion Audit Report

**Author:** Automated audit  
**Date:** 2026-09-26  
**Scope:** Complete codebase review of the data-ingestion pipeline  
**Branch:** `worktree-phase3-scraper-audit`

---

## A. What sources exist in `scraper/config/sources.py`?

Three sources are registered in the `SOURCES` dict (`scraper/config/sources.py:38-68`):

| Name | `has_official_api` | `scraping_permitted` | `base_url` | `method` |
|------|-------------------|---------------------|-----------|---------|
| `airline_a` | `True` | `False` | `https://api.example-airline-a.com` | `api` |
| `airline_b` | `False` | `False` | `https://www.example-airline-b.com` | `not_permitted` |
| `airline_c` | `False` | `False` | `https://www.example-airline-c.com` | `not_permitted` |

**`get_active_sources()`** filters on `method != "not_permitted"`, so only **`airline_a`** is returned as active.

Three additional adapter classes exist in `scraper/sources/` but are **not registered** in SOURCES or ADAPTERS:

| Adapter class | File | Internal name | Target |
|--------------|------|--------------|--------|
| `AirZenAdapter` | `airzen_adapter.py` | `airline_e` | local test server `/normal` |
| `FlySphereAdapter` | `flysphere_adapter.py` | `airline_d` | local test server `/delayed` |
| `JetVistaAdapter` | `jetvista_adapter.py` | `airline_c` | local test server `/normal` |

---

## B. Which actually collect real data from an external source?

**Zero.** No adapter in the current codebase fetches data from a real external airline API or website.

- `airline_a` in `main.py:27` is wired to `MockAirlineAAdapter` (hardcoded synthetic data).
- `airline_b` in `main.py:31` is wired to `AirlineBAdapter` (a template that raises `PermanentSourceError` because the URL contains `"example-airline"`).
- `airline_c` is `not_permitted` in config, so `get_active_sources()` skips it.
- `airzen_adapter.py`, `flysphere_adapter.py`, `jetvista_adapter.py` target a local test server (`five-airfare-test-sites`) and are not registered in `ADAPTERS`.

---

## C. Which are mock/stub/synthetic, which are templates, and which target test harnesses?

| Category | Adapter | File | Evidence |
|----------|---------|------|----------|
| **Mock/Synthetic** | `MockAirlineAAdapter` | `mock_api_source.py` | Returns hardcoded `base_fare=5000, taxes=500, total_fare=5500`, airline `"Mock Air"`. No network call. |
| **Template (API)** | `AirlineAAdapter` | `example_api_source.py` | Raises `PermanentSourceError("Placeholder API URL configured...")` when URL contains `"example-airline"`. Has full rate limiting, retry, and proper FareQuote field mapping. This is the correct skeleton for a real API source. |
| **Template (Scrape)** | `AirlineBAdapter` | `example_scrape_source.py` | Raises `PermanentSourceError("Placeholder scrape URL configured...")` on placeholder URLs. Has CAPTCHA/block detection, rate limiting, retry. Correct skeleton for permitted browser scraping. |
| **Test Harness** | `AirZenAdapter` | `airzen_adapter.py` | Playwright, targets local test server at `/normal`. Basic block detection. Sets `base_fare=price, total_fare=price` (no tax separation, `taxes` defaults to `0`). |
| **Test Harness** | `FlySphereAdapter` | `flysphere_adapter.py` | Playwright, targets test server at `/delayed`. No block detection. No tax separation. |
| **Test Harness** | `JetVistaAdapter` | `jetvista_adapter.py` | Playwright, targets test server at `/normal`. No block detection, no rate limiting, no retry. |

---

## D. What routes does the scraper cover today?

`scraper/scheduler/job_generator.py:10-17` defines:

```python
ROUTES = (
    ("DEL", "BOM"),
    ("DEL", "BLR"),
    ("BOM", "BLR"),
    ("DEL", "CCU"),
    ("BLR", "HYD"),
    ("MAA", "DEL"),
)
```

**Comparison with the APIx basket (from project spec and `index-engine`):**

| Route | APIx weight | In ROUTES? |
|-------|------------|------------|
| DEL → BOM | 0.25 | ✅ |
| DEL → BLR | 0.25 | ✅ |
| BOM → BLR | 0.20 | ✅ |
| **DEL → HYD** | **0.15** | **❌ MISSING** |
| **BOM → HYD** | **0.15** | **❌ MISSING** |
| DEL → CCU | 0 (not in basket) | ✅ (extra) |
| BLR → HYD | 0 (not in basket) | ✅ (extra) |
| MAA → DEL | 0 (not in basket) | ✅ (extra) |

**CRITICAL:** Two routes that carry 30% combined weight in the APIx basket (DEL→HYD, BOM→HYD) are **not scraped**. Three routes are scraped but have zero weight in the index. The index engine will compute APIx from only 70% of the intended basket.

---

## E. What airlines does the scraper cover?

Only **"Mock Air"** — the hardcoded airline name in `MockAirlineAAdapter` (`mock_api_source.py:19`).

No real airline (IndiGo, Air India, SpiceJet, Akasa Air, Vistara, etc.) is currently being scraped.

---

## F. What booking windows / advance-purchase days are supported?

`scraper/scheduler/job_generator.py:9`:

```python
ADVANCE_WINDOWS = (45, 30, 15, 7, 1)
```

These correspond to the canonical windows: **T+1, T+7, T+15, T+30, T+45**.

**⚠️ Index engine mismatch:** `index-engine/src/index_engine/config.py:12` defaults to:

```python
SUPPORTED_BOOKING_WINDOWS: list = "T+7,T+15,T+30".split(",")
```

Only 3 of the 5 windows. T+1 and T+45 observations would be collected but **ignored by the index engine** unless this config is overridden at runtime.

---

## G. What is each source's data-field contract?

### FareQuote Pydantic model (`scraper/models/fare_quote.py`)

| Field | Type | Required | Default | Constraint |
|-------|------|----------|---------|------------|
| `source` | str | ✅ | — | |
| `origin` | str(3) | ✅ | — | Uppercased, IATA code |
| `destination` | str(3) | ✅ | — | Uppercased, IATA code, ≠ origin |
| `travel_date` | date | ✅ | — | |
| `observation_timestamp` | datetime | ✅ | — | Must be tz-aware |
| `advance_days` | int | ✅ | — | ≥ 0, validated against travel_date |
| `airline` | str | ✅ | — | |
| `flight_number` | str | ❌ | `None` | |
| `fare_class` | str | ✅ | `"Economy"` | |
| `cabin` | str | ✅ | `"Economy"` | |
| `fare_family` | str | ❌ | `None` | |
| `stops` | int | ✅ | `0` | |
| `departure_time` | str | ❌ | `None` | |
| `arrival_time` | str | ❌ | `None` | |
| `base_fare` | Decimal | ✅ | — | > 0 |
| `taxes` | Decimal | ✅ | `0` | ≥ 0 |
| `other_charges` | Decimal | ✅ | `0` | ≥ 0 |
| `total_fare` | Decimal | ✅ | — | > 0, ≈ base + taxes + charges ±₹1 |
| `currency` | str(3) | ✅ | `"INR"` | |
| `availability` | str | ✅ | `"available"` | |
| `search_profile` | str | ✅ | `"one_way_economy_1pax"` | |

### What each adapter actually provides:

| Field | MockAirlineA | AirlineA (template) | AirlineB (template) | AirZen | FlySphere | JetVista |
|-------|-------------|--------------------|--------------------|--------|-----------|---------|
| base_fare | ✅ hardcoded 5000 | ✅ from JSON | ✅ = total_fare | ✅ = price | ✅ = price | ✅ = price |
| taxes | ✅ hardcoded 500 | ✅ from JSON | ❌ hardcoded 0 | **❌ missing (defaults 0)** | **❌ missing (defaults 0)** | **❌ missing (defaults 0)** |
| other_charges | ❌ defaults 0 | ✅ from JSON | ❌ defaults 0 | ❌ defaults 0 | ❌ defaults 0 | ❌ defaults 0 |
| airline | "Mock Air" | from JSON | from DOM | "AirZen" | "FlySphere" | "JetVista" |
| flight_number | ❌ | ✅ from JSON | ❌ | ❌ | ❌ | ❌ |
| fare_class | defaults | ✅ from JSON | "Economy" | defaults | defaults | defaults |
| cabin | defaults | ✅ from JSON | "Economy" | defaults | defaults | defaults |
| block detection | N/A | N/A (API) | ✅ 5 indicators | ✅ 1 indicator | ❌ none | ❌ none |
| rate limiting | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |
| retry | ❌ | ✅ 3 attempts | ✅ 2 attempts | ❌ | ❌ | ❌ |

---

## H. Do any sources separate base_fare, taxes, and surcharges?

**Only two** adapter classes handle fare separation properly:

1. **`AirlineAAdapter` (template)** — Maps `base_fare`, `taxes`, `other_charges` separately from the API JSON response (`example_api_source.py:77-79`).
2. **`MockAirlineAAdapter`** — Uses hardcoded values: `base_fare=5000, taxes=500, total_fare=5500`.

All three test-site adapters (AirZen, FlySphere, JetVista) set `base_fare = total_fare` with no tax component, meaning `taxes` defaults to `Decimal("0")`. This **passes** Pydantic validation (the reconciliation check `total ≈ base + taxes + charges` succeeds) but produces **incorrect fare decomposition**.

---

## I. Is there normalisation/cleaning logic? Where?

Yes. `cleaning-normalization/service.py` contains:

- **Airport normalization:** `AIRPORT_MAPPING` dict converting city names to IATA codes (DELHI→DEL, MUMBAI→BOM, etc.)
- **Airline normalization:** `AIRLINE_MAPPING` dict converting names/IATA codes to canonical names (INDIGO→IndiGo, 6E→IndiGo, etc.)
- **Currency normalization:** `standardize_currency()` — stub, only passes through INR
- **Validation:** `validate_record()` checks mandatory fields and non-positive fares
- **Outlier flagging:** Tukey 1.5×IQR method on `total_fare`
- **Pipeline:** `process_raw_data(df)` runs validation → normalization → outlier flagging → returns `(cleaned_df, rejected_df)`

---

## J. Does the cleaning module write back to the database?

**No.** `process_raw_data()` accepts a pandas DataFrame and returns two DataFrames (cleaned, rejected). It has **no database connection, no import of psycopg2/SQLAlchemy, and no write call**. It is a pure in-memory transform with no I/O.

---

## K. Is there deduplication? Where and how?

Yes, in **two places**:

1. **Application-level dedup** (`scraper/db/models.py:80-87`): `save_fare_quote()` calls `get_existing_observation()` which queries by `(source, origin, destination, travel_date, advance_days)`. If a match exists, the new record is skipped and `"duplicate"` status is returned.

2. **Database-level dedup** (`scraper/db/models.py:42-47`): `UniqueConstraint("source", "origin", "destination", "travel_date", "advance_days", name="uq_observation_key")` on `fare_observations`.

**NOTE:** The dedup key does **not** include `airline` or `flight_number`. If a route has multiple airlines/flights, only the first observation per source/route/date/window is kept. For a system that eventually needs per-airline granularity, this is a significant limitation.

---

## L. Is there an outlier-detection step?

Yes, in `cleaning-normalization/service.py:55-59`:

```python
Q1 = df['total_fare'].quantile(0.25)
Q3 = df['total_fare'].quantile(0.75)
IQR = Q3 - Q1
upper_bound = Q3 + 1.5 * IQR
```

Records above `upper_bound` get `outlier_flag = True` but are **not removed** — they stay in the cleaned output.

**⚠️ This outlier detection is unreachable** because the cleaning module is completely disconnected from the live pipeline (see Question S).

---

## M. Is there rate-limiting logic?

Yes. `scraper/core/rate_limiter.py` provides a thread-safe `RateLimiter` class with per-source minimum-interval enforcement using `time.monotonic()`.

**Which adapters actually use it:**

| Adapter | Uses rate limiter? |
|---------|-------------------|
| `MockAirlineAAdapter` | ❌ No |
| `AirlineAAdapter` (template) | ✅ Yes — `rate_limiter.wait_if_needed()` |
| `AirlineBAdapter` (template) | ✅ Yes — `rate_limiter.wait_if_needed()` |
| `AirZenAdapter` | ❌ No |
| `FlySphereAdapter` | ❌ No |
| `JetVistaAdapter` | ❌ No |

Only the two production templates use rate limiting. The mock adapter and all three test-harness adapters do not.

---

## N. Does the data actually reach `fare_observations` in PostgreSQL?

**Conditionally.** The scraper's default database is **SQLite** (`scraper/db/database.py` defaults to `sqlite:///airfare_data.db`). Only when the `DATABASE_URL` env var is set to a PostgreSQL connection string does data reach PostgreSQL's `fare_observations` table.

When it does reach PostgreSQL, the trigger `trg_ingest_fare_observation` (`database/init.sql:151-155`) copies each INSERT into the PascalCase `FareObservations` table, auto-creating `Routes` and `Airlines` entries.

---

## O. Does the data reach `RepresentativeFares`?

Only via an explicit separate pipeline step. `representative-fare-engine/service.py` reads from `FareObservations` (PascalCase — the trigger-populated table) and writes to `RepresentativeFares`. It is invoked by `scheduler/jobs.py:19-26` via `subprocess.run()`.

**Prerequisite chain:** Scraper → `fare_observations` → PG trigger → `FareObservations` → representative-fare-engine → `RepresentativeFares`.

If the scraper writes to SQLite (default), nothing reaches `RepresentativeFares`.

---

## P. Does the data reach `AirfareIndices`?

Via two independent paths, neither currently producing meaningful results:

1. **`scraper/aggregate.py`** — Direct SQL that joins `fare_observations` with `Routes` and `BasePeriods` to calculate indices. This is a standalone script, not called by the scheduler.

2. **`index-engine/`** — The formal index-engine module with the Laspeyres strategy (`index-engine/src/index_engine/strategies/laspeyres.py`). Called by the scheduler via `index-engine/run_test.py`.

Both paths require real data in `fare_observations` and populated `BasePeriods`. With only mock data (airline "Mock Air", hardcoded ₹5500), any index values would be meaningless.

---

## Q. Do any scrapers bypass the cleaning-normalisation pipeline?

**All of them.** See Question S for the full analysis.

---

## R. Do any scrapers bypass `RepresentativeFares` and write directly to `AirfareIndices`?

**No.** No adapter writes to `AirfareIndices` directly. The only paths to `AirfareIndices` are:
1. `scraper/aggregate.py` (standalone, not invoked by scheduler)
2. `index-engine/run_test.py` (invoked by scheduler)

Both read from pre-existing fare/representative-fare data.

---

## S. Does any scraper bypass the cleaning-normalisation module entirely?

**YES — ALL OF THEM.**

The pipeline as implemented:

```
Scraper (main.py)
  → FareQuote (Pydantic validation)
  → is_sane_fare() (sanity checks)
  → save_fare_quote() → fare_observations table (SQLAlchemy)
  → PG trigger → FareObservations table
  → representative-fare-engine reads from FareObservations
  → index-engine reads from RepresentativeFares
```

The `cleaning-normalization/service.py` module is **entirely disconnected**:
- It is not imported by any file in `scraper/`
- It is not called by `scheduler/jobs.py`
- It is not referenced in `scheduler/scheduler.py`
- `grep -r "cleaning" scraper/` and `grep -r "process_raw_data"` yield no results outside the module itself

**Impact:** Airport name normalization (DELHI→DEL), airline name normalization (INDIGO→IndiGo), currency conversion, and Tukey IQR outlier flagging **never execute** on any ingested data.

---

## T. Does any scraper compute APIx directly?

**No.** No adapter or scraper module calculates APIx values. The two files that touch index calculations are:

1. `scraper/aggregate.py` — A standalone script (not a scraper) that computes AirfareIndices from existing DB data
2. `scraper/test_windows_apix.py` — A test script that exercises the index-engine

Neither is a source/adapter. No adapter returns or writes index values.

---

## U. What are the biggest data-contract gaps between what the scraper produces and what `RepresentativeFares` / the index engine expects?

### Gap 1: Cleaning pipeline is disconnected (CRITICAL)
The cleaning-normalization module never runs. All data reaches downstream consumers raw.

### Gap 2: Missing basket routes (CRITICAL)
DEL→HYD (weight 0.15) and BOM→HYD (weight 0.15) are absent from `ROUTES`, so the index can only operate on 70% of the intended basket.

### Gap 3: Booking window mismatch (HIGH)
The scraper collects 5 windows (T+1, T+7, T+15, T+30, T+45) but the index engine defaults to only 3 (T+7, T+15, T+30). T+1 and T+45 observations are collected but potentially ignored.

### Gap 4: No real data (CRITICAL)
Only `MockAirlineAAdapter` is active, producing identical `₹5500` fares for every route/date/window. No meaningful indices can be computed.

### Gap 5: Dual fare_observations tables with schema drift
- Scraper writes to `fare_observations` (lowercase) with one schema (23 columns including `other_charges`, `fare_family`, etc.)
- PG trigger copies to `FareObservations` (PascalCase) with a different schema (15 columns, uses `tax` instead of `taxes`, no `other_charges`, no `fare_family`)
- The trigger **drops** `other_charges`, `fare_family`, `departure_time`, `arrival_time`, `stops`, `cabin`, `search_profile`, `availability`, `flight_number` — those fields are lost

### Gap 6: `RepresentativeFares` schema mismatch
`init.sql:57-63` defines `RepresentativeFares` with only `(route_id, booking_window, date, median_fare)`.
`representative-fare-engine/service.py:65-73` tries to INSERT into columns including `fare_class`, `observation_count`, `calculation_method`, `status` and uses `ON CONFLICT (route_id, date, booking_window, fare_class)` — but these columns and constraint **don't exist in init.sql**. This INSERT will fail at runtime.

### Gap 7: `AirfareIndices` schema mismatch
`init.sql:65-71` defines `AirfareIndices` without a `UNIQUE` constraint on `date`, but `scraper/aggregate.py:37` uses `ON CONFLICT (date)` — this requires a unique index that doesn't exist in the DDL.

### Gap 8: Test-site adapters don't separate fares
AirZen, FlySphere, JetVista all set `base_fare = total_fare, taxes = 0`. The index methodology that relies on fare decomposition would get distorted inputs.

### Gap 9: SQLite as default database
`scraper/db/database.py` defaults to SQLite. The PG trigger, `FareObservations` (PascalCase), `RepresentativeFares`, and `AirfareIndices` only exist in PostgreSQL. Unless `DATABASE_URL` is explicitly set, no downstream pipeline stage has data to process.

---

## V. Single highest-priority Phase 3 task

**Wire the cleaning-normalization module into the live pipeline** — specifically, insert it between the scraper's `save_fare_quote()` and the data that `representative-fare-engine` consumes.

### Rationale

This is the single change that, once done, enables everything else:

1. **It's the only structural blocker.** Even once a real source is connected, data will flow through to the index engine without any normalization, outlier detection, or validation beyond the basic Pydantic/sanity checks. Airport names from real sources may arrive as "DELHI" or "New Delhi" rather than "DEL" — without the cleaning module, these won't match Routes entries and will be invisible to the index.

2. **It's already written.** The `process_raw_data()` function exists and handles normalization, validation, and outlier flagging. It just needs to be called.

3. **It unblocks confidence in all other data.** Connecting a real source (the next task after this) without cleaning in place means raw, unnormalized, un-outlier-checked data enters `RepresentativeFares` and corrupts index calculations.

4. **It's low-risk.** The module is a pure transform — wiring it in doesn't change the scraper, the database schema, or the index engine. It's an addition to the pipeline, not a rewrite.

### Suggested approach (not a code change — just the plan):

- After scraper writes to `fare_observations`, run `process_raw_data()` on new records
- Mark processed rows (add a `cleaned` boolean or timestamp column)
- Have `representative-fare-engine` read only cleaned/validated rows
- Alternatively: make cleaning a step in `scheduler/jobs.py` between scraper and aggregation

---

## Additional Findings: Bugs & Security Issues

### 🐛 BUG: `scheduler/scheduler.py:6` imports non-existent `test_job`

```python
from scheduler.jobs import test_job, run_scraper_job, ...
```

`test_job` is not defined in `scheduler/jobs.py`. This causes an `ImportError` on any import of `scheduler.scheduler`, making the entire scheduler module **non-functional**.

### 🔒 SECURITY: Hardcoded database credentials

| File | Line | Value |
|------|------|-------|
| `scraper/aggregate.py` | 14 | `postgresql://admin:password123@localhost:5432/sih_db` |
| `scraper/test_windows_apix.py` | 12 | `postgresql://admin:password123@localhost:5432/sih_db` (presumed, same pattern) |
| `index-engine/src/index_engine/config.py` | 6 | `postgresql://admin:password123@localhost:5432/sih_db` |

These should be replaced with env-var-only loading (no fallback credentials), consistent with the pattern already used by `representative-fare-engine/service.py` and `scheduler/config.py`.

### ⚠️ MockAirlineAAdapter does not extend `SourceAdapter`

`mock_api_source.py:5`: `class MockAirlineAAdapter:` — it's a plain class, not inheriting from `SourceAdapter` (`sources/base.py`). The three test-site adapters do inherit from it. This inconsistency means type checking and interface enforcement are bypassed for the only active adapter.

---

## Summary Matrix

| Question | Finding |
|----------|---------|
| A — Sources in config | 3 configured (airline_a, b, c) + 3 unregistered adapters (airzen, flysphere, jetvista) |
| B — Real external data | **ZERO** — none collect from a real airline |
| C — Mock vs template vs test | 1 mock, 2 templates, 3 test-harness |
| D — Routes covered | 6 routes, but **DEL→HYD and BOM→HYD (30% basket weight) missing** |
| E — Airlines covered | Only "Mock Air" |
| F — Booking windows | T+1, T+7, T+15, T+30, T+45 (but index engine defaults to only 3) |
| G — Field contract | Strong Pydantic model with 21 fields, full validation |
| H — Fare separation | Only template adapter does it properly; test adapters set base=total |
| I — Cleaning logic | Exists in `cleaning-normalization/service.py` |
| J — Cleaning writes to DB | No — pure in-memory transform |
| K — Dedup | Yes — app-level check + DB unique constraint |
| L — Outlier detection | Yes (Tukey 1.5×IQR) — but unreachable |
| M — Rate limiting | Yes in core module — used only by templates |
| N — Data reaches PG? | Only if `DATABASE_URL` is set (defaults to SQLite) |
| O — Data reaches RepresentativeFares? | Only via separate pipeline step, requires PG |
| P — Data reaches AirfareIndices? | Via aggregate.py or index-engine, requires populated BasePeriods |
| Q — Bypass cleaning? | **YES — all scrapers bypass it** |
| R — Direct write to AirfareIndices? | No |
| S — Full bypass of cleaning? | **YES — cleaning module is completely disconnected** |
| T — Scraper computes APIx? | No |
| U — Biggest gaps | Disconnected cleaning, missing basket routes, no real sources, schema drift, booking window mismatch |
| V — Highest priority | **Wire cleaning-normalization into the live pipeline** |
