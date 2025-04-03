"""
Script to fix integrations with missing user_id values.
This script assigns a default user to orphaned integrations or removes them if no user exists.
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

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_integrations():
    """Fix integrations with null user_id values."""
    with SessionLocal() as session:
        try:
            # Check if any users exist
            users_result = session.execute(text("SELECT id FROM users LIMIT 1"))
            user = users_result.fetchone()
            
            if not user:
                logger.error("No users found in the database. Cannot fix integrations.")
                return
                
            default_user_id = user[0]
            logger.info(f"Using default user ID: {default_user_id}")
            
            # Find integrations with null user_id
            null_integrations_result = session.execute(
                text("SELECT id FROM integrations WHERE user_id IS NULL")
            )
            null_integrations = null_integrations_result.fetchall()
            
            if not null_integrations:
                logger.info("No integrations with null user_id found. Database is already clean.")
                return
                
            logger.info(f"Found {len(null_integrations)} integrations with null user_id.")
            
            # Update integrations with null user_id
            session.execute(
                text("UPDATE integrations SET user_id = :user_id WHERE user_id IS NULL"),
                {"user_id": default_user_id}
            )
            
            # Commit the transaction
            session.commit()
            logger.info(f"Successfully updated {len(null_integrations)} integrations with user_id = {default_user_id}")
            
            # Verify the fix
            verification_result = session.execute(
                text("SELECT COUNT(*) FROM integrations WHERE user_id IS NULL")
            )
            remaining_null = verification_result.scalar()
            
            if remaining_null > 0:
                logger.warning(f"There are still {remaining_null} integrations with null user_id.")
            else:
                logger.info("All integrations now have a valid user_id.")
            
        except Exception as e:
            session.rollback()
            logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting integration user_id fix script...")
    fix_integrations()
    logger.info("Script completed.") 