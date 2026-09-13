# Agent Handover: Representative Fare Engine

**Status:** Implementation Complete / Ready for Integration
**Branch:** `feature/representative-fare-engine`

## 1. Summary of Changes
The engine now acts as a stable aggregation layer. It reads cleaned fare observations from `FareObservations` and produces reliable fare statistics in `RepresentativeFares`.

## 2. To: Cleaning & Normalization Agents
*   **Role:** You feed this engine.
*   **Data Contract:**
    *   The engine expects `FareObservations` to be fully cleaned, deduplicated, and normalized (specifically currency).
    *   If `total_fare` is `NULL` or `<= 0`, the record will be discarded by the engine.
    *   **Crucial:** Ensure consistent mapping of grouping keys:
        *   `route_id`
        *   `travel_date`
        *   `booking_window`
        *   `fare_class` (If this deviates, the grouping mechanism will fail).
*   **Reminder:** Do not rely on this engine for data cleaning. Pre-validation is strictly your responsibility.

## 3. To: Index Construction Engine Agents
*   **Role:** You consume this engine.
*   **Data Contract:**
    *   Read from the `RepresentativeFares` table.
    *   The engine guarantees a **Median Total Fare** based on at least 2 valid observations.
    *   **Traceability:** Use `observation_count` and `calculation_method` to assess data confidence before applying route weights.
    *   **Architecture Boundary:** This engine **REPRESENTS PRICE**, it **NEVER CALCULATES THE INDEX**.
        *   You (the Index Engine) MUST apply DGCA route weights, calculate the Laspeyres aggregation, and handle base-period comparisons.
        *   Do not delegate index-calculation logic to this module.

## 4. Database Schema Integration (Summary)
The `RepresentativeFares` table has been updated to support traceability/idempotency:

| Column | Used By | Description |
| :--- | :--- | :--- |
| `route_id`, `date`, `booking_window`, `fare_class` | Both | Unique grouping key (enforced by `UNIQUE` constraint). |
| `median_fare` | Index Engine | The representative fare value. |
| `observation_count` | Index Engine | Metric for confidence/data density assessment. |
| `calculation_method` | Audit | Defaults to `MEDIAN_TOTAL_FARE`. |
| `status` | Audit | Defaults to `VALID`. |

---

### Integration Recommendation
*   **Idempotency:** The aggregation service uses `INSERT ON CONFLICT` based on `(route_id, date, booking_window, fare_class)`. If cleaned observations change, re-running the aggregation will correctly update the existing record.
*   **Traceability:** If the Index Engine encounters a suspicious Representative Fare, use the unique grouping key to join back to the underlying `FareObservations` to inspect individual prices.

---
*If you are an agent tasked with maintaining this pipeline, please refer to `/representative-fare-engine/README.md` for architectural context and `/prompts/rep_fare_engine_agent.md` for role-specific idioms.*
