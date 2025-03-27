"""
Main application module.
Entry point for the FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routes
from app.routes import dashboard, youtube, sales, auth, utm

# Import database initialization
from app.database import engine, Base

app = FastAPI(
    title="Insyte.io Dashboard API",
    description="Backend API for the Insyte.io Dashboard that helps online coaches, creators, and agencies track and analyze their performance metrics.",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
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

@app.on_event("startup")
def startup():
    """
    Initialize application on startup.
    Creates database tables if they don't exist.
    """
    # Create tables - using synchronous SQLAlchemy
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    """Root endpoint for API health check."""
    return {"status": "online", "message": "Insyte.io Dashboard API is running"}
