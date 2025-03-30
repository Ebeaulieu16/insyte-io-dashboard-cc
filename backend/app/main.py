"""
Main application module.
Entry point for the FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv
import traceback
from fastapi.responses import JSONResponse
from fastapi import Request, status
from starlette.middleware.sessions import SessionMiddleware
import secrets

# Load environment variables
load_dotenv()

# Set up logging - Enhanced for better error reporting
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)
logger.info(f"Starting application with log level: {log_level}")

# Import routes
from app.routes import dashboard, youtube, sales, auth, utm, calcom, user_auth

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

# Generate a secret key for sessions or use the JWT_SECRET
secret_key = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
logger.info("Adding SessionMiddleware to application")
app.add_middleware(
    SessionMiddleware,
    secret_key=secret_key,
    max_age=3600,  # 1 hour session timeout
    same_site="lax",  # Allows cookies during redirects for OAuth flows
    https_only=os.getenv("ENV", "development").lower() == "production"  # Secure in production
)

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
# Allow both the configured URL and localhost for development
allowed_origins = [frontend_url, "http://localhost:3000", "*"]  # Add wildcard for development
if "," in frontend_url:  # Handle comma-separated list of URLs
    allowed_origins = frontend_url.split(",") + ["http://localhost:3000", "*"]

logger.info(f"Configuring CORS with allowed origins: {allowed_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Use list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"],  # Expose these headers to the frontend
)

# Include all routers
app.include_router(dashboard.router)
app.include_router(youtube.router)
app.include_router(sales.router)
app.include_router(auth.router)
app.include_router(utm.router)
app.include_router(calcom.router)
app.include_router(user_auth.router)

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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    Logs the full traceback and returns a JSON response.
    """
    error_details = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error(f"Unhandled exception: {str(exc)}\n{error_details}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please check server logs for details."}
    )
