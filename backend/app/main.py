"""
Main application module.
Entry point for the FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routes
from app.routes import dashboard, youtube, sales, auth, utm

# Import database initialization
from app.database import engine, Base

# Try to import the payments router - this may fail if migrations are incomplete
try:
    from app.routes import payments
    payments_router_available = True
except ImportError as e:
    logger.warning(f"Payments router not available: {e}")
    payments_router_available = False

app = FastAPI(
    title="Insyte.io Dashboard API",
    description="Backend API for the Insyte.io Dashboard that helps online coaches, creators, and agencies track and analyze their performance metrics.",
    version="0.1.0",
)

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
# Allow both the configured URL and localhost for development
allowed_origins = [frontend_url, "http://localhost:3000"]
if "," in frontend_url:  # Handle comma-separated list of URLs
    allowed_origins = frontend_url.split(",") + ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Use list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(dashboard.router)
app.include_router(youtube.router)
app.include_router(sales.router)
app.include_router(auth.router)
app.include_router(utm.router)

# Include payments router if available
if payments_router_available:
    try:
        app.include_router(payments.router)
        logger.info("Payments router successfully included")
    except Exception as e:
        logger.error(f"Error including payments router: {e}")

@app.on_event("startup")
async def startup():
    """
    Initialize application on startup.
    Creates database tables if they don't exist.
    """
    # Create tables - using synchronous SQLAlchemy approach
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

@app.get("/")
async def root():
    """Root endpoint for API health check."""
    return {"status": "online", "message": "Insyte.io Dashboard API is running"}
