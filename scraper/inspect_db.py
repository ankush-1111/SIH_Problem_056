import sqlite3
import sqlalchemy
from sqlalchemy import create_engine, text

# Get engine from backend settings (reuse logic)
try:
    # Assuming backend-api/app.py sets up SQLAlchemy, but I'll replicate the connection
    # Let's try to infer db path - common for SIH projects to use a file-based sqlite if not specified
    # The app code defaults to postgresql://admin:password123@localhost:5432/sih_db
    # If the user isn't running postgres, it might be failing or empty
    
    # Check if there's a local .db file in project root
    print("Checking for local database files...")
    import os
    for file in os.listdir("."):
        if file.endswith(".db") or file.endswith(".sqlite"):
            print(f"Found database file: {file}")
            
except Exception as e:
    print(f"Error inspecting DB: {e}")

