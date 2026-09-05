# Agent Setup Configuration

This file tells an AI assistant how to configure the environment for the current teammate. 
Fill out the configuration section below before asking the agent to start.

### 1. Configuration (Fill this out)
- **Teammate Name/Role:** [e.g., Ankush - Scraper Team]
- **Primary Feature Folder:** [e.g., /scraper/]

### 2. Instructions for the Agent
Based on the configuration above, please perform the following steps immediately after reading this file:

1.  **Set Context:** Focus file operations primarily on the **Primary Feature Folder** defined above.
2.  **Environment Check:**
    - Verify that `docker-compose.yml` exists in the `/database/` folder.
    - Ask the user if they want to start the database using `docker-compose -f database/docker-compose.yml up -d`.
    - Check if they have created a local `.env` file based on `.env.example`.
3.  **Branch Check:** Ensure the user is currently on a branch related to their feature (e.g., `feature/...`). If not, advise them which branch to switch to.
4.  **Workflow Confirmation:** Briefly summarize the git workflow (Commit to feature -> Push -> PR to develop) and ask if they have any questions before they begin coding.
