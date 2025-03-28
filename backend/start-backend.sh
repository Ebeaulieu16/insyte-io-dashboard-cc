#!/bin/bash

# Exit on error
set -e

echo "Starting application setup..."

# Get directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

# Apply database migrations
echo "Applying database migrations..."
alembic upgrade head

# Start the application
echo "Starting the FastAPI application..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 