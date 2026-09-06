# Cleaning & Normalization Component

## Overview
The Cleaning & Normalization component cleans raw flight fare data and enforces schema consistency.

## Data Architecture
Processes raw data from staging tables and writes structured data to production tables in the `database`.

## Developer/Agent Onboarding
- **Prompt Reference**: See `prompts/cleaning_agent.md`.
- **Implementation**: Ensure data validation ensures clean, queryable data for analytic components.
- **Connectivity**: Use the standard connection string from `database/README.md`.

## Automated Workflow
- The data is cleaned and inserted into the production PostgreSQL container.
- Once optimized, analytic engines can trigger their processing tasks.
