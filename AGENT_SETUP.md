# Agent Setup Configuration

This file tells an AI assistant how to configure the environment for the current teammate. 
Fill out the configuration section below before asking the agent to start.

### 1. Configuration (Fill this out)
- **Teammate Name/Role:** [e.g., Ankush - Scraper Team]
- **Primary Feature Folder:** [e.g., /scraper/]

### 2. Instructions for the Agent
Based on the configuration above, please perform the following steps immediately after reading this file:

1.  **Identify OS & Prerequisites (Required Step 1):**
    - Ask the user: "What Operating System are you using? (Windows/Mac/Linux)"
    - Based on the response, provide direct download links for **Docker Desktop** and **Git** for their specific OS.
    - Inform the user: "Please install these now and type 'Done' when you have finished the installation."

2.  **Environment Automation (Required Step 2 - Executed after user types 'Done'):**
    - Once the user confirms installation, proceed with these automated tasks:
      - **Database (.env):** Check for the `.env` file. If missing, create it using `.env.example` as a template and ask the user to input the database credentials if they haven't already.
      - **Start Database:** Execute `docker-compose -f database/docker-compose.yml up -d`.
      - **Initialize Database:** After the container is running and healthy, execute the `database/init.sql` script to create the tables.
      - **Verify:** Confirm with the user that the database is running successfully.

3.  **Branch Check & Workflow:**
    - Ensure the user is currently on their feature branch.
    - Briefly summarize the Git workflow (Commit locally -> Push -> PR to develop-> Review).
