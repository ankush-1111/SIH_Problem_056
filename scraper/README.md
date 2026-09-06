# Scraper Component

## Overview
The Scraper component is responsible for fetching raw flight fare data from designated sources.

## Data Architecture
Data scraped by this component is ingested directly into the `database`'s staging tables.

## Developer/Agent Onboarding
- **Prompt Reference**: See `prompts/scraper_agent.md`.
- **Implementation**: Ensure all fetching logic implements rate-limiting and error handling.
- **Connectivity**: Use the standard connection string from `database/README.md`.

## Automated Workflow
- The data is inserted into the PostgreSQL container.
- Once inserted, the `scheduler` may trigger a `cleaning-normalization` task based on the status update in the staging table.
