"""
SQLAlchemy models package.
This package contains all database models for the application.
"""

from app.models.video_link import VideoLink
from app.models.click import Click
from app.models.call import Call, CallStatus
from app.models.payment import Payment
from app.models.video_analytics import VideoAnalytics
from app.models.integration import Integration, IntegrationType
from app.models.user import User

# Import all models here for easy access in other parts of the application
__all__ = [
    "VideoLink",
    "Click", 
    "Call", 
    "CallStatus",
    "Payment",
    "VideoAnalytics",
    "Integration",
    "IntegrationType",
    "User"
]
