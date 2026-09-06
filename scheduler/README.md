# Scheduler Component

## Overview
The Scheduler orchestrates automated scraping and processing tasks.

## Data Architecture
Monitors DB status flags and triggers component executions.

## Developer/Agent Onboarding
- **Prompt Reference**: See `prompts/scheduler_agent.md`.
- **Implementation**: Ensure triggers are fault-tolerant.

## Automated Workflow
- The scheduler runs periodically and kicks off pipeline tasks.
