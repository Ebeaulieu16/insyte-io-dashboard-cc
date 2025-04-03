"""
Script to check the current state of integrations and their user assignments.
This script helps verify if integrations are properly tied to their respective users.

Usage:
    python check_integration_userids.py
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("integration_check.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable not set")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_integration_ownership():
    """
    Check the current state of integrations in the database.
    Reports on:
    1. Total number of users
    2. Total number of integrations
    3. Breakdown of integrations by user
    4. Any integrations without a valid user_id
    """
    db = SessionLocal()
    
    try:
        # First, check if the users table exists
        check_users = text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users')")
        result = db.execute(check_users).scalar()
        
        if not result:
            logger.error("Users table does not exist. Check cannot proceed.")
            return
        
        # Check if the integrations table exists
        check_integrations = text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'integrations')")
        result = db.execute(check_integrations).scalar()
        
        if not result:
            logger.error("Integrations table does not exist. Check cannot proceed.")
            return
        
        # Get all active users
        users_query = text("SELECT id, email FROM users WHERE is_active = TRUE ORDER BY id")
        users = db.execute(users_query).fetchall()
        
        if not users:
            logger.warning("No active users found.")
            return
        
        logger.info(f"Found {len(users)} active users")
        
        # Get total integration count
        integrations_count_query = text("SELECT COUNT(*) FROM integrations")
        total_integrations = db.execute(integrations_count_query).scalar()
        logger.info(f"Total integrations: {total_integrations}")
        
        # Get count of integrations without valid user_id
        null_integrations_query = text("SELECT COUNT(*) FROM integrations WHERE user_id IS NULL")
        null_integrations = db.execute(null_integrations_query).scalar()
        if null_integrations > 0:
            logger.warning(f"Found {null_integrations} integrations with NULL user_id")
        else:
            logger.info("No integrations with NULL user_id found")
        
        # Get breakdown of integrations by user
        print("\n=== Integrations By User ===")
        for user in users:
            user_id = user[0]
            email = user[1]
            
            # Get integrations for this user
            user_integrations_query = text("""
                SELECT platform, status, account_name 
                FROM integrations 
                WHERE user_id = :user_id
                ORDER BY platform
            """)
            user_integrations = db.execute(user_integrations_query, {"user_id": user_id}).fetchall()
            
            print(f"\nUser: {email} (ID: {user_id})")
            if user_integrations:
                print(f"  Total integrations: {len(user_integrations)}")
                for i, integration in enumerate(user_integrations, 1):
                    platform = integration[0]
                    status = integration[1]
                    account_name = integration[2] or "Unnamed"
                    print(f"  {i}. {platform}: {status} - {account_name}")
            else:
                print("  No integrations found")
        
        # Get integrations per platform
        platforms_query = text("""
            SELECT platform, COUNT(*) 
            FROM integrations 
            GROUP BY platform 
            ORDER BY COUNT(*) DESC
        """)
        platforms = db.execute(platforms_query).fetchall()
        
        print("\n=== Integrations By Platform ===")
        for platform in platforms:
            name = platform[0]
            count = platform[1]
            print(f"{name}: {count} integrations")
            
    except Exception as e:
        logger.error(f"Error during integration check: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting integration ownership check")
    check_integration_ownership()
    logger.info("Integration ownership check completed") 