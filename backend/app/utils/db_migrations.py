"""
Database migration utilities for handling schema changes at runtime.
These migrations run automatically during application startup when needed.
"""

import logging
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def ensure_extra_data_column(db: Session):
    """
    Ensures that the extra_data column exists in the integrations table.
    This is a critical column for storing API keys and other integration data.
    
    Args:
        db: SQLAlchemy database session
    """
    try:
        # Check if the integrations table exists
        check_table = text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'integrations')")
        table_exists = db.execute(check_table).scalar()
        
        if not table_exists:
            logger.warning("Integrations table does not exist yet, skipping extra_data column check")
            return
        
        # Check if the extra_data column exists
        check_column = text("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'integrations' AND column_name = 'extra_data'
            )
        """)
        column_exists = db.execute(check_column).scalar()
        
        if column_exists:
            logger.info("extra_data column already exists in integrations table")
            return
        
        # Add the extra_data column if it doesn't exist
        logger.warning("extra_data column is missing from integrations table - adding it now")
        
        # For PostgreSQL, use JSONB type for better performance
        # Try using direct SQL ALTER TABLE statement
        try:
            add_column = text("""
                ALTER TABLE integrations 
                ADD COLUMN extra_data JSONB
            """)
            db.execute(add_column)
            logger.info("Successfully added extra_data column using ALTER TABLE")
        except Exception as e1:
            logger.warning(f"Failed to add column with standard approach: {str(e1)}")
            
            # Try with IF NOT EXISTS (supported in newer PostgreSQL)
            try:
                add_column_alt = text("""
                    ALTER TABLE integrations 
                    ADD COLUMN IF NOT EXISTS extra_data JSONB
                """)
                db.execute(add_column_alt)
                logger.info("Successfully added extra_data column using IF NOT EXISTS")
            except Exception as e2:
                logger.error(f"Failed to add column with IF NOT EXISTS: {str(e2)}")
                raise
        
        # Create index for better performance on JSON queries
        try:
            create_index = text("""
                CREATE INDEX idx_integrations_extra_data 
                ON integrations USING GIN (extra_data)
            """)
            db.execute(create_index)
            logger.info("Created GIN index on extra_data column")
        except Exception as e:
            # Try with IF NOT EXISTS for index
            try:
                create_index_alt = text("""
                    CREATE INDEX IF NOT EXISTS idx_integrations_extra_data 
                    ON integrations USING GIN (extra_data)
                """)
                db.execute(create_index_alt)
                logger.info("Created GIN index on extra_data column using IF NOT EXISTS")
            except Exception as e2:
                logger.warning(f"Could not create index on extra_data: {str(e2)}")
        
        # Update existing integrations to initialize extra_data from other columns
        update_sql = text("""
            UPDATE integrations
            SET extra_data = jsonb_build_object(
                'api_key', COALESCE(api_key, ''),
                'source', 'migration'
            )
            WHERE extra_data IS NULL
        """)
        
        try:
            db.execute(update_sql)
            logger.info("Updated existing integrations with initial extra_data values")
        except Exception as e:
            logger.warning(f"Could not initialize extra_data values: {str(e)}")
        
        # Commit all changes
        db.commit()
        logger.info("Successfully added extra_data column to integrations table")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error ensuring extra_data column: {str(e)}")
        # Don't raise the exception - we want the app to continue starting up

def run_all_runtime_migrations(db: Session):
    """
    Run all runtime migrations in the correct order.
    This function is called during application startup.
    
    Args:
        db: SQLAlchemy database session
    """
    logger.info("Running runtime database migrations...")
    
    # Add all migrations here in order
    ensure_extra_data_column(db)
    
    logger.info("Runtime database migrations completed") 