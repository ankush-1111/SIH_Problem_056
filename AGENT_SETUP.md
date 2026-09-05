# Agent Setup Configuration

This file tells an AI assistant how to configure the environment for the current teammate. 
Fill out the configuration section below before asking the agent to start.

### 1. Configuration (Fill this out)
- **Teammate Name/Role:** [e.g., Ankush - Scraper Team]
- **Primary Feature Folder:** [e.g., /scraper/]

### 2. Instructions for the Agent
Based on the configuration above, please perform the following steps immediately after reading this file:

1.  **Generate Setup Checklist:**
    Promptly generate a "Manual Setup Checklist" for the user below. Specifically include:
    - **Manual Prerequisites:** Explicitly list installation links for Docker Desktop and Git (Explain that the user MUST install these manually).
    - **Commands for Agent Execution:** Provide the exact CLI commands (like `.env` creation templates and `docker-compose` commands) needed to get the environment ready. 
    - **Database Initialization:** Instruct the agent to inform the user about running the `database/init.sql` script once the container is up.
2.  **Set Context:** Focus file operations primarily on the **Primary Feature Folder** defined above.
3.  **Branch Check:** Ensure the user is currently on a branch related to their feature (e.g., `feature/...`). If not, advise them which branch to switch to.
4.  **Workflow Confirmation:** Briefly summarize the git workflow (Commit to feature -> Push -> PR to develop) and ask if they have any questions before they begin coding.
