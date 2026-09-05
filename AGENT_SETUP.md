# Agent Onboarding Script

This file contains the instructions for any AI agent that initializes a new team member's workspace.

### Instructions for the Agent:
Do not ask the user to edit this file. **Automatically initiate the following interview flow:**

1.  **Welcome & Identify:**
    - Greet the team member.
    - Ask for their: **Name**, **Role**, and **Assigned Feature Folder** (e.g., "scraper").
    - Validate the inputs (e.g., ensure the feature folder actually exists).

2.  **OS & Prerequisites (If not already installed):**
    - Ask the user: "What Operating System are you using? (Windows/Mac/Linux)"
    - Provide direct links to download **Docker Desktop** and **Git** for their OS.
    - Ask the user to confirm when they have finished installation (e.g., 'Done').

3.  **Automated Setup (Once confirmed):**
    - **Branch Check:** Check if the user is on their assigned branch. If not, inform them how to switch (e.g., `git checkout feature/<assigned-feature>`).
    - **Database (.env):** Check for the `.env` file. If missing, create it using `.env.example` as a template.
    - **Database Container:** Prompt the user: "Would you like me to start the local database container for you?" (If yes, run `docker-compose -f database/docker-compose.yml up -d`).
    - **Initialize Tables:** Instruct the user on how to run `init.sql` to initialize the database tables.

4.  **Workflow Confirmation:** Briefly summarize the Git workflow (Commit locally -> Push -> PR to develop) and ask if they have any questions before they begin coding.
