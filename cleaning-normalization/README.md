# Cleaning & Normalization Engine

## Overview
This engine transforms raw airfare observations into a standardized, auditable dataset suitable for statistical analysis.

## Core Objective
Produce a dataset that is:
- Correct, consistent, and comparable.
- Traceable and auditable.
- Statistically defensible for Airfare Price Index (APIx) construction.

## Golden Rules
1.  **Never modify raw data:** Keep Layer 1 (Raw) immutable.
2.  **Traceability:** Every transformation must be explainable (rule applied + reason).
3.  **Standardization:** Use the defined Standard Data Model. Maps to `RECORD_ID`, `TOTAL_FARE`, `CURRENCY` (INR), travel/observation dates, etc.
4.  **No Silent Deletion:** Reject/flag records only with a documented reason.
5.  **No Inventory of Data:** Do not invent components (base fare, fees) if missing. Use NULL.
6.  **Deterministic:** Cleaning rules must be reproducible across time.

## Data Pipeline
1.  **Profiling**: Profile raw data before any cleaning.
2.  **Cleaning**: Handle missing values, deduplicate (logic-conscious), and flag invalid records (negative fares, impossible dates).
3.  **Outlier Handling**: Flag/reject based on statistical methods (IQR/Deviation) only if truly invalid.
4.  **Normalization**: Standardize currencies (INR), locations (IATA codes), airlines (mapping tables), and dates (YYYY-MM-DD).

## Output Deliverables
- `cleaned_dataset`
- `analytics_ready_dataset`
- `rejected_records` (with reasons)
- `data_quality_report`
