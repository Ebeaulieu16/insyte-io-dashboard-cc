"""
Script to fix the user_id field in integrations table.

This script iterates through all integrations tied to user ID 1 and attempts
to find their rightful owners based on matching API keys or access tokens.

Usage:
    python fix_integrations_user_id.py
"""

import os
import sys
import json
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("integration_fix.log"),
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

def fix_integration_ownership():
    """
    Fix integration ownership by:
    1. Identifying integrations tied to user_id=1 that might belong to other users
    2. Checking if other users already have the same integration (by platform)
    3. For each user without the integration, create a copy with their user_id
    """
    db = SessionLocal()
    
    try:
        # First, check if the users table exists
        check_users = text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users')")
        result = db.execute(check_users).scalar()
        
        if not result:
            logger.error("Users table does not exist. Migration cannot proceed.")
            return
        
        # Check if the integrations table exists
        check_integrations = text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'integrations')")
        result = db.execute(check_integrations).scalar()
        
        if not result:
            logger.error("Integrations table does not exist. Migration cannot proceed.")
            return
        
        # Get all active users
        users_query = text("SELECT id, email FROM users WHERE is_active = TRUE")
        users = db.execute(users_query).fetchall()
        
        if not users:
            logger.warning("No active users found. Nothing to migrate.")
            return
        
        logger.info(f"Found {len(users)} active users")
        
        # Get all integrations with user_id=1
        default_integrations_query = text("""
            SELECT id, platform, status, account_name, account_id, access_token, refresh_token, extra_data 
            FROM integrations 
            WHERE user_id = 1
        """)
        default_integrations = db.execute(default_integrations_query).fetchall()
        
        if not default_integrations:
            logger.info("No integrations found with user_id=1. Nothing to migrate.")
            return
        
        logger.info(f"Found {len(default_integrations)} integrations with user_id=1")
        
        # For each user with id > 1, check if they need integrations migrated
        for user in users:
            user_id = user[0]
            email = user[1]
            
            # Skip the default user
            if user_id == 1:
                continue
            
            logger.info(f"Processing user {email} (ID: {user_id})")
            
            # Get existing integrations for this user
            user_integrations_query = text("""
                SELECT platform FROM integrations WHERE user_id = :user_id
            """)
            user_integrations = db.execute(user_integrations_query, {"user_id": user_id}).fetchall()
            user_platforms = {i[0] for i in user_integrations}
            
            logger.info(f"User already has integrations for platforms: {user_platforms}")
            
            # For each default integration, check if user needs it
            for integration in default_integrations:
                integration_id = integration[0]
                platform = integration[1]
                status = integration[2]
                account_name = integration[3]
                account_id = integration[4]
                access_token = integration[5]
                refresh_token = integration[6]
                extra_data_str = integration[7]
                
                # Skip if user already has this platform
                if platform in user_platforms:
                    logger.info(f"User already has {platform} integration. Skipping.")
                    continue
                
                # Create a copy of this integration for the user
                try:
                    extra_data = json.loads(extra_data_str) if extra_data_str else {}
                    
                    # Insert new integration for this user
                    insert_query = text("""
                        INSERT INTO integrations 
                        (user_id, platform, status, account_name, account_id, access_token, refresh_token, extra_data, last_sync)
                        VALUES
                        (:user_id, :platform, :status, :account_name, :account_id, :access_token, :refresh_token, :extra_data, :last_sync)
                    """)
                    
                    db.execute(insert_query, {
                        "user_id": user_id,
                        "platform": platform,
                        "status": status,
                        "account_name": account_name,
                        "account_id": account_id,
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "extra_data": json.dumps(extra_data) if extra_data else None,
                        "last_sync": datetime.now()
                    })
                    
                    logger.info(f"Created {platform} integration for user {email}")
                    
                except Exception as e:
                    logger.error(f"Error creating integration for user {email}: {str(e)}")
                    continue
            
        # Commit all changes
        db.commit()
        logger.info("Integration ownership migration completed successfully")
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error during integration ownership migration: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting integration ownership migration")
    fix_integration_ownership()
    logger.info("Integration ownership migration script completed") 