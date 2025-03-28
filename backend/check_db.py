#!/usr/bin/env python3
import os, sys
from dotenv import load_dotenv
import psycopg

def check_database_connection():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return False

    try:
        # Connect to the database
        conn = psycopg.connect(database_url)
        print("Database connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    success = check_database_connection()
    if success:
        print("All database checks passed.")
        sys.exit(0)
    else:
        print("Database check failed. Please check your connection settings.")
        sys.exit(1)
