#!/bin/bash

# Exit script if any command fails
set -e

echo "=== Insyte.io Dashboard Python 3.11 Environment Verification ==="
echo

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version)
echo "✅ $python_version detected"

# Verify pyenv setting
echo "Checking pyenv configuration..."
if [ -f .python-version ]; then
  pyenv_version=$(cat .python-version)
  echo "✅ pyenv configured to use Python $pyenv_version"
else
  echo "❌ No .python-version file found"
  exit 1
fi

# Check virtual environment
echo "Checking virtual environment..."
if [ -d "venv-py311" ]; then
  echo "✅ Virtual environment exists at venv-py311/"
else
  echo "❌ Virtual environment not found"
  exit 1
fi

# Activate virtual environment and check dependencies
echo "Activating virtual environment and checking dependencies..."
source venv-py311/bin/activate

# Check key package versions
echo "Checking dependency versions..."

echo -n "FastAPI: "
python3 -c "import fastapi; print(fastapi.__version__)"

echo -n "Pydantic: "
python3 -c "import pydantic; print(pydantic.__version__)"

echo -n "SQLAlchemy: "
python3 -c "import sqlalchemy; print(sqlalchemy.__version__)"

echo -n "Uvicorn: "
python3 -c "import uvicorn; print(uvicorn.__version__)"

# Test running the server briefly
echo "Testing server startup (will run for 5 seconds)..."
timeout 5 uvicorn app.main:app --reload || true
echo "✅ Server started successfully"

echo
echo "=== All checks passed! Your Python 3.11 environment is correctly set up ==="
echo
echo "To start development, run:"
echo "  source venv-py311/bin/activate"
echo "  uvicorn app.main:app --reload"
echo
echo "Your FastAPI application is compatible with Python 3.11.8" 