"""
Database configuration module.
Sets up the SQLAlchemy engine and session for PostgreSQL using psycopg3.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL will come from environment variables in production
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://emilebeaulieu@localhost:5432/insyte_dashboard")

# Use the psycopg driver with SQLAlchemy
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

# Create engine
engine = create_engine(
    DATABASE_URL, 
    echo=True,  # Set to False in production
)

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
