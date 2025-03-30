"""
Database configuration module.
Sets up the SQLAlchemy engine and session for PostgreSQL using psycopg3.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)

# Database URL will come from environment variables in production
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://emilebeaulieu@localhost:5432/insyte_dashboard")

logger.info(f"Initializing database connection with URL type: {DATABASE_URL.split('://')[0] if '://' in DATABASE_URL else 'unknown'}")

# Special handling for Render PostgreSQL URLs (which may start with postgres://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    logger.info("Converted postgres:// URL to postgresql://")

# Use the psycopg driver with SQLAlchemy
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
    logger.info("Using postgresql+psycopg:// driver")

# Create engine with proper SSL configuration for Render
try:
    logger.info("Creating database engine...")
    engine = create_engine(
        DATABASE_URL, 
        echo=os.getenv("ENV", "development").lower() != "production",  # False in production, True in development
        pool_pre_ping=True,  # Test connections before using them
        connect_args={} if os.getenv("ENV", "development").lower() != "production" else {
            "sslmode": "require"  # Required for Render PostgreSQL
        }
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Error creating database engine: {str(e)}")
    raise

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create declarative base for models
Base = declarative_base()

# Dependency for FastAPI endpoints
def get_db():
    """Dependency to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
