"""
Script to clean up demo data for users with real integrations.
This ensures that once a user has real integrations, they no longer see demo data.
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

def clean_demo_data():
    """
    Clean up demo data for users with real integrations.
    This removes all demo data entries from various tables if the user has actual integrations.
    """
    with SessionLocal() as session:
        try:
            # Find users with real integrations
            users_with_integrations_result = session.execute(
                text("""
                    SELECT DISTINCT user_id 
                    FROM integrations 
                    WHERE status = 'connected' OR is_connected = TRUE
                """)
            )
            
            users_with_integrations = [row[0] for row in users_with_integrations_result]
            
            if not users_with_integrations:
                logger.info("No users with active integrations found.")
                return
                
            logger.info(f"Found {len(users_with_integrations)} users with active integrations.")
            
            # For each user with integrations, identify and remove demo data
            for user_id in users_with_integrations:
                logger.info(f"Cleaning demo data for user_id: {user_id}")
                
                # Here we need to clean all tables that might contain demo data
                # Video analytics table (typically contains YouTube demo data)
                try:
                    result = session.execute(
                        text("""
                            DELETE FROM video_analytics 
                            WHERE user_id = :user_id AND is_demo = TRUE
                        """),
                        {"user_id": user_id}
                    )
                    logger.info(f"Removed {result.rowcount} demo video analytics entries for user {user_id}")
                except Exception as e:
                    logger.warning(f"Could not clean video_analytics table: {str(e)}")
                
                # Clicks table (typically contains UTM demo data)
                try:
                    result = session.execute(
                        text("""
                            DELETE FROM clicks 
                            WHERE user_id = :user_id AND is_demo = TRUE
                        """),
                        {"user_id": user_id}
                    )
                    logger.info(f"Removed {result.rowcount} demo clicks entries for user {user_id}")
                except Exception as e:
                    logger.warning(f"Could not clean clicks table: {str(e)}")
                
                # Payments table (typically contains sales demo data)
                try:
                    result = session.execute(
                        text("""
                            DELETE FROM payments 
                            WHERE user_id = :user_id AND is_demo = TRUE
                        """),
                        {"user_id": user_id}
                    )
                    logger.info(f"Removed {result.rowcount} demo payments entries for user {user_id}")
                except Exception as e:
                    logger.warning(f"Could not clean payments table: {str(e)}")
                
                # Calls table (typically contains calendly/cal.com demo data)
                try:
                    result = session.execute(
                        text("""
                            DELETE FROM calls 
                            WHERE user_id = :user_id AND is_demo = TRUE
                        """),
                        {"user_id": user_id}
                    )
                    logger.info(f"Removed {result.rowcount} demo calls entries for user {user_id}")
                except Exception as e:
                    logger.warning(f"Could not clean calls table: {str(e)}")
            
            # Commit all changes
            session.commit()
            logger.info("Successfully cleaned demo data for users with real integrations")
            
        except Exception as e:
            session.rollback()
            logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting demo data cleanup script...")
    clean_demo_data()
    logger.info("Script completed.") 