# Agent Setup Configuration

This file tells an AI assistant how to configure the environment for the current teammate. 
Fill out the configuration section below before asking the agent to start.

### 1. Configuration (Fill this out)
- **Teammate Name/Role:** [e.g., Ankush - Scraper Team]
- **Primary Feature Folder:** [e.g., /scraper/]

### 2. Instructions for the Agent
Based on the configuration above, please perform the following steps immediately after reading this file:

1.  **Set Context:** Focus file operations primarily on the **Primary Feature Folder** defined above.
2.  **Manual Environment Setup (Guide the user):**
    - **Docker:** Check if Docker Desktop is installed. If not, guide the user to download and install it from https://www.docker.com/products/docker-desktop/. Explain that this is necessary to run the database.
    - **Database (.env):** Check if a `.env` file exists in the root directory (based on `.env.example`). If not, guide the user to create it:
      - Create a new file named `.env`.
      - Copy the content of `.env.example` into it.
    - **Start Database:** Once Docker is ready, ask the user if they want to start the database using `docker-compose -f database/docker-compose.yml up -d`.
3.  **Branch Check:** Ensure the user is currently on a branch related to their feature (e.g., `feature/...`). If not, advise them which branch to switch to.
4.  **Workflow Confirmation:** Briefly summarize the git workflow (Commit to feature -> Push -> PR to develop) and ask if they have any questions before they begin coding.
