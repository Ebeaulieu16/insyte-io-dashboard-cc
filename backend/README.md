# Insyte.io Dashboard Backend

The FastAPI backend for the Insyte.io Dashboard, helping online coaches, creators, and agencies track and analyze their performance metrics.

## Project Structure

```
/backend
└── /app
    ├── main.py                # Main application entry point
    ├── database.py            # Database connection setup
    ├── /models                # SQLAlchemy models
    ├── /schemas               # Pydantic schemas
    ├── /routes                # API endpoints
    │   ├── dashboard.py       # Dashboard metrics endpoints
    │   ├── youtube.py         # YouTube metrics endpoints
    │   ├── sales.py           # Sales funnel metrics endpoints
    │   ├── auth.py            # Platform integration endpoints
    │   └── utm.py             # UTM tracking endpoints
    ├── /utils                 # Helper functions
    └── __init__.py
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL:
- Make sure PostgreSQL is installed and running
- Create a database called `insyte_dashboard`
- Set environment variables or update connection details in `database.py`

4. Run the application:
```bash
cd backend
uvicorn app.main:app --reload
```

5. Access the API documentation at http://localhost:8000/docs

## API Endpoints

- `/api/dashboard` - Global KPIs and metrics overview
- `/api/sales` - Sales funnel metrics
- `/api/youtube` - YouTube performance metrics
- `/auth/{platform}` - Platform integration (YouTube, Stripe, Calendly, Cal.com)
- `/api/links/create` - Create UTM tracking links
- `/go/{slug}` - UTM link tracking and redirection

## Environment Variables

Create a `.env` file in the `backend` directory with:

```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/insyte_dashboard
# Add other environment variables as needed
``` 