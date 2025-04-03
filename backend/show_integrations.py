#!/usr/bin/env python
"""
Script to show all integrations in the database with their associated users.
Useful for monitoring and troubleshooting integration issues.
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

def show_integrations():
    """Display all integrations in the database with their associated users."""
    with SessionLocal() as session:
        try:
            # Get all users for reference
            users_result = session.execute(text("SELECT id, email FROM users"))
            users = {user[0]: user[1] for user in users_result.fetchall()}
            
            logger.info(f"Found {len(users)} users in the database")
            
            # Get all integrations
            integrations_result = session.execute(
                text("""
                    SELECT id, platform, user_id, status, account_name, is_connected, last_sync
                    FROM integrations
                    ORDER BY user_id, platform
                """)
            )
            
            integrations = integrations_result.fetchall()
            
            if not integrations:
                logger.info("No integrations found in the database")
                return
                
            logger.info(f"Found {len(integrations)} integrations in the database")
            logger.info("\nIntegration Summary:")
            logger.info("-" * 80)
            logger.info(f"{'ID':<6} {'Platform':<10} {'User ID':<8} {'User Email':<25} {'Status':<12} {'Connected':<10} {'Account Name':<25}")
            logger.info("-" * 80)
            
            # Group integrations by user_id
            user_integrations = {}
            for integration in integrations:
                user_id = integration[2]
                if user_id not in user_integrations:
                    user_integrations[user_id] = []
                user_integrations[user_id].append(integration)
            
            # Display integrations by user
            for user_id, user_integs in user_integrations.items():
                user_email = users.get(user_id, "Unknown")
                
                for integration in user_integs:
                    int_id = integration[0]
                    platform = integration[1]
                    status = integration[3] if integration[3] else "Unknown"
                    is_connected = "Yes" if integration[5] else "No"
                    account_name = integration[4] if integration[4] else "N/A"
                    
                    logger.info(f"{int_id:<6} {platform:<10} {user_id:<8} {user_email:<25} {status:<12} {is_connected:<10} {account_name:<25}")
                
                logger.info("-" * 80)  # Separator between users
            
            # Print summary stats
            platform_counts = {}
            for integration in integrations:
                platform = integration[1]
                if platform not in platform_counts:
                    platform_counts[platform] = 0
                platform_counts[platform] += 1
            
            logger.info("\nIntegration Counts by Platform:")
            for platform, count in platform_counts.items():
                logger.info(f"{platform}: {count} integrations")
            
            # Check for integrations without user_id
            null_user_id_query = "SELECT COUNT(*) FROM integrations WHERE user_id IS NULL"
            null_result = session.execute(text(null_user_id_query))
            null_count = null_result.scalar()
            
            if null_count > 0:
                logger.warning(f"Found {null_count} integrations with NULL user_id")
                
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting integrations display script...")
    show_integrations()
    logger.info("Script completed.") 