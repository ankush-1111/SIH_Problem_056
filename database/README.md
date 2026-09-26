# Database & Connectivity Guide

## Overview
We are using **PostgreSQL 16** via Docker. Every team member has a local, independent database instance.

## Connecting to your DB

### 1. Using a GUI Tool (Recommended)
Download **[DBeaver](https://dbeaver.io/)** (or pgAdmin) and connect using these settings:
- **Host:** `localhost`
- **Port:** `5432`
- **Database:** `sih_db` (or whatever you set in `.env`)
- **Username:** `admin` (or whatever you set in `.env`)
- **Password:** `password123` (or whatever you set in `.env`)

### 2. Using Python/App Code
Use the `.env` file to manage your connection string. 
Example (SQLAlchemy):
```python
DATABASE_URL = "postgresql://user:password@host:port/db" # Set this to your database URL
```

### 3. Troubleshooting
- **Is the DB running?** Run: `docker ps`
- **See logs:** Run: `docker logs sih_db`
- **Wipe and restart (If you break your local test data):**
  ```bash
  docker-compose -f database/docker-compose.yml down -v
  docker-compose -f database/docker-compose.yml up -d
  ```
