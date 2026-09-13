# Real-time Airfare Price Index for India (APIx)
### Augmentation of the Consumer Price Index (CPI) — Smart India Hackathon (SIH-056)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 1. Project Overview

In the official Consumer Price Index (CPI) basket of India compiled by the Ministry of Statistics and Programme Implementation (MoSPI), airfare price collection currently relies primarily on periodic or manual survey samplings. This latency fails to capture the dynamic, algorithmically fluctuating pricing behavior inherent to Indian civil aviation.

**SIH Problem Statement 056** requires:
> "Development of a Real-time Airfare Price Index for India through Automated Web Scraping of Airline and Online Travel Aggregator Portals for Augmentation of the Consumer Price Index (CPI)."

This repository implements an end-to-end, statistically sound, real-time pipeline that ingests domestic airfares across key commercial routes, cleanses anomalies, computes representative median fares across advance purchase horizons, and produces a Laspeyres Airfare Price Index (**APIx**) pegged to **Base Period: January 2026 = 100.00**.

---

## 2. System Architecture & Data Flow

```mermaid
graph TD
    A[Airline & OTA Sources] -->|Scrape / Ingest| B[Scraper Engine / Staging]
    B -->|Schema Validation| C[(PostgreSQL: fare_observations)]
    C -->|Trigger / Normalization| D[(PostgreSQL: FareObservations)]
    D -->|Median Aggregation| E[Representative Fare Engine]
    E -->|Upsert Group Medians| F[(PostgreSQL: RepresentativeFares)]
    F -->|Laspeyres Aggregation| G[Index Engine]
    G -->|Daily / Weekly / Monthly Index| H[(PostgreSQL: AirfareIndices)]
    H -->|Expose JSON REST API| I[FastAPI Backend :8001]
    I -->|Query & Visualize| J[Streamlit Dashboard :8501]
    K[Scheduler / Cron] -.->|Orchestrate 08:00 IST| B
    K -.->|Trigger| E
    K -.->|Trigger| G
```

### Data Transformation Pipeline
1. **Raw Observation Layer (`fare_observations`)**: Ingests raw flight quotes containing origin, destination, travel date, advance purchase window, airline, cabin, flight number, base fare, taxes, and total payable fare.
2. **Normalized Observations (`FareObservations`)**: Relational schema normalized against `Routes` and `Airlines` master tables via PostgreSQL triggers.
3. **Representative Fares (`RepresentativeFares`)**: Deterministic median total fare aggregated across routes, dates, and advance purchase horizons with sample size thresholds ($N \ge 2$).
4. **Index Engine (`AirfareIndices`)**: Aggregative Laspeyres price index calculated across active route volume shares.
5. **Analytics & Backtest (`ExternalBenchmarks`)**: Dynamic correlation, MAE, and RMSE benchmarking against DGCA domestic fare survey baselines.

---

## 3. Mathematical & Statistical Methodology

### A. Laspeyres Price Index Formula
The Headline Airfare Price Index ($\text{APIx}$) is calculated using the weighted aggregative Laspeyres formula:

$$\text{APIx}_t = \frac{\sum_{r \in R} w_r \cdot \bar{P}_{r,t}}{\sum_{r \in R} w_r \cdot \bar{P}_{r,0}} \times 100$$

Where:
- $w_r$: Statistical weight of route $r$ based on DGCA annual passenger traffic volume share ($\sum_{r \in R} w_r = 1.0000$).
- $\bar{P}_{r,t}$: Representative fare for route $r$ on date $t$, defined as the mean across observed canonical booking windows.
- $\bar{P}_{r,0}$: Base period representative fare for route $r$ (January 2026 baseline across matched booking windows).
- **Base Period**: January 2026 = 100.00 (Dimensionless index; no currency units).

### B. Canonical Booking Horizons
In accordance with civil aviation pricing dynamics, the analytical engine monitors strictly 5 canonical advance purchase horizons:
- **T+1**: Emergency / Last-minute travel (1 day before departure)
- **T+7**: Short-term advance booking (7 days before departure)
- **T+15**: Medium-term advance booking (15 days before departure)
- **T+30**: Standard advance planning (30 days before departure)
- **T+45**: Early-bird leisure booking (45 days before departure)

### C. Mathematical Contributor Decomposition
The analytical engine strictly separates two distinct attribution concepts:
1. **Daily Change Attribution** (Explains why $\text{APIx}$ moved from $t-1$ to $t$):
   $$\Delta C_r = \frac{w_r \cdot (\bar{P}_{r,t} - \bar{P}_{r,t-1})}{B_0} \times 100$$
   *Strict Mathematical Closure*: $\sum_{r} \Delta C_r \equiv \text{APIx}_t - \text{APIx}_{t-1}$ (within $0.0000$ numerical precision).
2. **Base Level Composition** (Explains why $\text{APIx}$ is above or below 100):
   $$C_r^{\text{level}} = \frac{w_r \cdot (\bar{P}_{r,t} - \bar{P}_{r,0})}{B_0} \times 100$$
   *Strict Mathematical Closure*: $\sum_{r} C_r^{\text{level}} \equiv \text{APIx}_t - 100.00$.

---

## 4. Development & Synthetic Data Disclosure

> [!NOTE]
> **Prototype Environment Disclosure**:
> During development and evaluation, the pipeline operates with **synthetic test carrier feeds** (`Mock Air`, `AeroNation`) and **simulated carrier data** (`Air India`, `IndiGo`, `SpiceJet`), alongside a **simulated DGCA domestic survey calibration series** (35 paired observation dates).
> 
> The core cleaning, representative fare, Laspeyres index, and attribution engines are fully production-grade and will process live web-scraped carrier observations without architectural or mathematical modifications.

---

## 5. Quick Start & Setup Guide

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL 16 (or Dockerized PostgreSQL)

### Step 1: Clone Repository & Configure Environment
```bash
git clone https://github.com/your-org/SIH-056.git
cd SIH-056
cp .env.example .env
```
Ensure your `.env` contains:
```env
DB_USER=admin
DB_PASSWORD=password123
DB_NAME=sih_db
DATABASE_URL=postgresql://admin:password123@localhost:5432/sih_db
```

### Step 2: Start PostgreSQL Container
```bash
docker compose -f database/docker-compose.yml up -d
```

### Step 3: Initialize Database & Seed Baseline Data
```bash
# Initialize schema and triggers
docker exec -i sih_db psql -U admin -d sih_db < database/init.sql

# Seed base period (Jan 2026), DGCA benchmarks, and historical indices
python database/seed_base.py
python database/seed_benchmark.py
python database/regenerate_indices.py
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Start Backend API (FastAPI)
```bash
python backend-api/app.py
# API runs on http://127.0.0.1:8001 (Swagger docs at /docs)
```

### Step 6: Start Streamlit Dashboard
```bash
streamlit run dashboard-ui/app.py
# UI opens automatically at http://localhost:8501
```

---

## 6. Automated Test Suites

The codebase includes an exhaustive verification harness covering statistical correctness, data contracts, and dashboard integration:

```bash
# 1. 15-Point Statistical & Methodology Audit
python testing/test_audit_15.py

# 2. Section 20 Specification Validation Checklist
python testing/test_section20_validation.py

# 3. Dashboard API Contract Integration Tests
python testing/test_dashboard_integration.py

# 4. Mathematical Linearity and Sensitivity Tests
python testing/test_sensitivity.py

# 5. Core Laspeyres Correctness Tests
python testing/test_apix_correctness.py
```

---

## 7. Git Workflow & Release Policy

- **`develop`**: Primary integration branch. All feature contributions merge here via Pull Request.
- **`main`**: Production-ready release branch. Merges from `develop` into `main` require full verification test passes.
- **Rules**: Never force-push or commit secrets (`.env` is strictly ignored).

