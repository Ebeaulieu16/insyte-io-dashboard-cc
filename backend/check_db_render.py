"""
Database connection checker script for Render deployment.
Run this script to verify database connectivity.
"""

import sys
import os
import traceback
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test connection to the database and print detailed results."""
    print("Database Connection Test")
    print("========================")
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set.")
        return False
    
    # Print obfuscated URL (hide password)
    url_parts = database_url.split("://")
    if len(url_parts) > 1:
        protocol = url_parts[0]
        rest = url_parts[1]
        if "@" in rest:
            auth_part, server_part = rest.split("@", 1)
            if ":" in auth_part:
                username = auth_part.split(":", 1)[0]
                obfuscated_url = f"{protocol}://{username}:****@{server_part}"
            else:
                obfuscated_url = f"{protocol}://{auth_part}@{server_part}"
        else:
            obfuscated_url = database_url
    else:
        obfuscated_url = database_url
    
    print(f"Database URL type: {url_parts[0] if len(url_parts) > 1 else 'unknown'}")
    print(f"Database URL: {obfuscated_url}")
    
    # Convert postgres:// to postgresql:// if needed
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://")
        print("Converted postgres:// URL to postgresql://")
    
    # Convert to use psycopg driver
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://")
        print("Using postgresql+psycopg:// driver")
    
    # Test connection
    try:
        print("\nAttempting to connect to database...")
        engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            connect_args={"sslmode": "require"}
        )
        
        # Try to connect and execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"Connection successful! Result: {result.scalar()}")
            
            # Test query against pg_tables to verify schema access
            tables_result = connection.execute(text(
                "SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema')"
            ))
            tables = tables_result.fetchall()
            
            print("\nDatabase Tables:")
            print("----------------")
            if tables:
                for table in tables:
                    print(f"Schema: {table[0]}, Table: {table[1]}")
            else:
                print("No user tables found in database.")
            
        print("\nAll database tests passed successfully!")
        return True
    except Exception as e:
        print(f"\nERROR: Database connection failed: {str(e)}")
        print("\nDetailed error trace:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1) 