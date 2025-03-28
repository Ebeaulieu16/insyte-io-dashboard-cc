# Render.com Deployment Guide

## Method 1: Using render.yaml (Recommended)

The simplest way to deploy is using the included render.yaml file, which defines your infrastructure.

### Steps:

1. **Push Your Code to GitHub**
   Make sure your code is in a GitHub repository.

2. **Create a Render Account**
   - Sign up at render.com
   - Verify your email

3. **Create a New Blueprint**
   - From your Render dashboard, click on "Blueprints" in the left menu
   - Click "New Blueprint Instance"
   - Connect to your GitHub repository
   - Select the repository containing your code

4. **Configure Your Blueprint**
   - Review the resources to be created
   - Fill in environment variables (DATABASE_URL, JWT_SECRET)
   - Click "Apply" to create all resources

## Method 2: Manual Deployment

If you prefer more control or need to customize your deployment, you can deploy each component separately.

### Step 1: Create a PostgreSQL Database

1. In your Render dashboard, click on "PostgreSQL"
2. Click "New PostgreSQL"
3. Fill in details (Name, Database, etc.)
4. Note the "Internal Database URL" for later use

### Step 2: Deploy the Backend API

1. Click "New Web Service"
2. Connect to your GitHub repository
3. Configure the service:
   - Name: insyte-backend
   - Runtime: Python 3
   - Build Command: cd backend && pip install -r requirements.txt
   - Start Command: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port \n4. Add environment variables (DATABASE_URL, JWT_SECRET, PYTHON_VERSION)

### Step 3: Deploy the Frontend

1. Click "New Static Site"
2. Connect to your GitHub repository
3. Configure the site:
   - Name: insyte-frontend
   - Build Command: cd frontend && npm install && npm run build
   - Publish Directory: frontend/build
4. Add environment variable REACT_APP_API_URL with your backend URL

## Troubleshooting

### CORS Issues

If you experience CORS issues, update your backend code to allow requests from your frontend domain in backend/app/main.py:


