#!/usr/bin/env python
"""
Fix the unique constraint on the integrations table.

This script:
1. Drops the unique constraint on the 'platform' column
2. Makes sure there's a composite constraint for platform and user_id

This allows multiple users to connect to the same platform.
"""

import os
import sys
import logging
from sqlalchemy import text
from app.database import SessionLocal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_integrations_constraint():
    """
    Fix the unique constraint on integrations table.
    - Drop the existing platform-only unique constraint
    - Ensure there's a proper composite constraint for user_id and platform
    """
    try:
        db = SessionLocal()
        
        try:
            # Check if the unique constraint ix_integrations_platform exists
            logger.info("Checking for existing unique constraint...")
            result = db.execute(text("""
                SELECT 1 FROM pg_constraint
                WHERE conname = 'ix_integrations_platform'
                  AND contype = 'u'
            """))
            
            constraint_exists = result.fetchone() is not None
            
            if constraint_exists:
                logger.info("Found unique constraint on platform column. Dropping it...")
                # Drop the unique constraint on platform
                db.execute(text("DROP INDEX IF EXISTS ix_integrations_platform"))
                logger.info("Unique constraint dropped successfully.")
            else:
                logger.info("No unique constraint found on platform column.")
            
            # Create a non-unique index on platform if one doesn't exist
            logger.info("Creating non-unique index on platform column...")
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_integrations_platform ON integrations (platform)"))
            
            # Create a composite unique constraint on user_id and platform
            logger.info("Creating composite unique constraint on user_id and platform...")
            db.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'uq_integrations_user_id_platform'
                    ) THEN
                        ALTER TABLE integrations 
                        ADD CONSTRAINT uq_integrations_user_id_platform 
                        UNIQUE (user_id, platform);
                    END IF;
                END
                $$;
            """))
            
            # Commit the transaction
            db.commit()
            logger.info("Constraints fixed successfully!")
            
            # Verify the user_id column exists and has proper values
            logger.info("Verifying user_id column...")
            result = db.execute(text("""
                SELECT COUNT(*) FROM integrations
                WHERE user_id IS NULL
            """))
            null_count = result.fetchone()[0]
            
            if null_count > 0:
                logger.info(f"Found {null_count} rows with NULL user_id. Updating them...")
                db.execute(text("UPDATE integrations SET user_id = 1 WHERE user_id IS NULL"))
                db.commit()
                logger.info("Updated NULL user_id values to 1")
            else:
                logger.info("All integrations have a valid user_id value.")
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error fixing integrations constraint: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting integrations constraint fix...")
    success = fix_integrations_constraint()
    
    if success:
        logger.info("✅ Successfully fixed integrations constraint!")
        sys.exit(0)
    else:
        logger.error("❌ Failed to fix integrations constraint!")
        sys.exit(1) 