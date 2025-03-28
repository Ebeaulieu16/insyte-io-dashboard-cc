#!/bin/bash

# Full-stack application starter script
# This script starts both the backend and frontend applications

# Colors for better readability
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Print header
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}    INSYTE.IO DASHBOARD STARTER SCRIPT     ${NC}"
echo -e "${BLUE}============================================${NC}"


# Function to handle errors
handle_error() {
    echo -e "${RED}ERROR: $1${NC}"
    exit 1
}

# Change to backend directory
cd backend || handle_error "Could not change to backend directory"

# Check backend environment
if [ ! -f ".env" ]; then
    if [ -f ".env-example" ]; then
        echo -e "${YELLOW}Warning: .env file not found, copying from .env-example${NC}"
        cp .env-example .env
        echo -e "${YELLOW}Please update the .env file with your actual configuration${NC}"
    else
        handle_error "No .env or .env-example file found in backend directory"
    fi
fi


# Setup Python virtual environment
if [ ! -d "../venv-py311" ]; then
    echo -e "${GREEN}Creating Python virtual environment...${NC}"
    python3 -m venv ../venv-py311 || handle_error "Failed to create virtual environment"
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source ../venv-py311/bin/activate || handle_error "Failed to activate virtual environment"

# Install Python dependencies
echo -e "${GREEN}Installing backend dependencies...${NC}"
pip install -r requirements.txt || handle_error "Failed to install backend dependencies"


# Check database connection
echo -e "${GREEN}Checking database connection...${NC}"
python check_db.py
DB_CHECK=$?
if [ $DB_CHECK -ne 0 ]; then
    echo -e "${YELLOW}Database check failed. Starting server anyway, but you may encounter errors.${NC}"
fi

# Start backend in background
echo -e "${GREEN}Starting backend server...${NC}"
echo -e "${BLUE}Backend will be accessible at http://localhost:8000${NC}"
echo -e "${BLUE}API docs available at http://localhost:8000/docs${NC}"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Return to project root
cd ..


# Start frontend
echo -e "${GREEN}Setting up frontend...${NC}"
cd frontend || handle_error "Could not change to frontend directory"

# Install frontend dependencies
echo -e "${GREEN}Installing frontend dependencies...${NC}"
npm install || handle_error "Failed to install frontend dependencies"

# Start frontend
echo -e "${GREEN}Starting frontend server...${NC}"
echo -e "${BLUE}Frontend will be accessible at http://localhost:3000${NC}"
npm start

# When frontend is closed, kill the backend
echo -e "${GREEN}Shutting down backend server...${NC}"
kill $BACKEND_PID

