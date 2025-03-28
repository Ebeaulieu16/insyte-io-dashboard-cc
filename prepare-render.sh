#!/bin/bash

# Script to prepare the application for deployment to Render.com

# Colors for better readability
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Print header
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}    PREPARE FOR RENDER DEPLOYMENT SCRIPT    ${NC}"
echo -e "${BLUE}============================================${NC}"


# Create render.yaml file
echo -e "${GREEN}Creating render.yaml file for Render.com deployment...${NC}"

cat > render.yaml << EOL
services:
  - type: web
    name: insyte-backend
    runtime: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port \$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.8
      - key: DATABASE_URL
        sync: false
      - key: JWT_SECRET
        generateValue: true
    healthCheckPath: /

  - type: web
    name: insyte-frontend
    runtime: static
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: ./frontend/build
    envVars:
      - key: NODE_VERSION
        value: 20.10.0
      - key: REACT_APP_API_URL
        fromService:
          name: insyte-backend
          type: web
          property: url
EOL


# Create a Procfile for Render (alternative to render.yaml)
echo -e "${GREEN}Creating Procfile for alternative deployment method...${NC}"
cat > Procfile << EOL
web: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port \$PORT
EOL

# Create .env.production file for frontend
echo -e "${GREEN}Creating production environment files...${NC}"
cat > frontend/.env.production << EOL
REACT_APP_API_URL=\${REACT_APP_API_URL:-https://api.insyte.io}
EOL

# Prepare backend for production
echo -e "${GREEN}Updating backend database.py for production...${NC}"
cd backend

# Create or update requirements.txt
echo -e "${GREEN}Ensuring all dependencies are in requirements.txt...${NC}"
cat > requirements.txt << EOL
fastapi==0.95.2
uvicorn==0.24.0
sqlalchemy==2.0.39
psycopg==3.1.18
psycopg-binary==3.2.6
psycopg-pool==3.2.0
pydantic==1.10.8
python-dotenv==1.0.0
httpx==0.25.1
python-multipart==0.0.6
starlette==0.27.0
alembic==1.12.1
cryptography==42.0.4
pyjwt==2.8.0
gunicorn==21.2.0
EOL

# Return to root directory
cd ..

echo -e "${GREEN}Preparation for Render deployment complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Commit these changes to your repository"
echo -e "2. Create a new Render web service using your repository"
echo -e "3. Set up your environment variables in the Render dashboard"
echo -e "4. Deploy!"

