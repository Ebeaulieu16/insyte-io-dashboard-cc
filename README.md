# Insyte.io Dashboard

A full-stack dashboard application helping online coaches, creators, and agencies track and analyze their performance metrics.

## Project Structure

### Backend

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

### Frontend

```
/frontend
└── /src
    ├── /assets                # Static assets (images, fonts, etc.)
    ├── /components            # Reusable UI components
    ├── /context               # React context providers
    ├── /examples              # Example components from template
    ├── /layouts               # Page layouts
    │   ├── /dashboard         # Main dashboard layout
    │   ├── /sales             # Sales metrics layout
    │   ├── /youtube           # YouTube metrics layout
    │   ├── /utm               # UTM generator layout
    │   ├── /integrations      # Platform integrations layout
    │   ├── /recommendations   # Recommendations layout
    │   └── /deepView          # Detailed metrics view layout
    ├── /utils                 # Helper functions and API client
    ├── App.js                 # Main application component
    ├── index.js               # Entry point
    └── routes.js              # Application routes
```

## Setup

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv-py311
source venv-py311/bin/activate  # On Windows: venv-py311\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up PostgreSQL:
- Make sure PostgreSQL is installed and running
- Create a database called `insyte_dashboard`
- Set environment variables or update connection details in `.env`

4. Run the application:
```bash
cd backend
uvicorn app.main:app --reload
```

5. Access the API documentation at http://localhost:8000/docs

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm start
```

3. Access the frontend at http://localhost:3000

## API Endpoints

- `/api/dashboard` - Global KPIs and metrics overview
- `/api/sales` - Sales funnel metrics
- `/api/youtube` - YouTube performance metrics
- `/auth/{platform}` - Platform integration (YouTube, Stripe, Calendly, Cal.com)
- `/api/links/create` - Create UTM tracking links
- `/go/{slug}` - UTM link tracking and redirection

## Environment Variables

### Backend

Create a `.env` file in the `backend` directory with:

```
DATABASE_URL=postgresql://username:password@localhost:5432/insyte_dashboard
JWT_SECRET=your_jwt_secret
FRONTEND_URL=http://localhost:3000
```

### Frontend

Create a `.env` file in the `frontend` directory with:

```
REACT_APP_API_URL=http://localhost:8000
```

## Deployment

See `RENDER_DEPLOYMENT_CHECKLIST.md` for instructions on deploying to Render.com.
