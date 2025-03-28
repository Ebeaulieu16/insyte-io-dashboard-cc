#!/bin/bash

# Exit script if any command fails
set -e

echo "Setting up Python 3.11.8 virtual environment for Insyte.io Dashboard"

# Check if Python 3.11.8 is installed via pyenv
if ! pyenv versions | grep -q "3.11.8"; then
  echo "Error: Python 3.11.8 is not installed via pyenv."
  echo "Please complete the installation of Python 3.11.8 before running this script."
  exit 1
fi

# Set local Python version to 3.11.8
echo "Setting local Python version to 3.11.8..."
pyenv local 3.11.8

# Verify Python version
PYTHON_VERSION=$(python3 --version)
echo "Using $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv-py311" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv-py311
else
  echo "Virtual environment already exists at venv-py311"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv-py311/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Verify installations
echo "Verifying installations..."
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"
python -c "import pydantic; print(f'Pydantic version: {pydantic.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy version: {sqlalchemy.__version__}')"

echo ""
echo "Setup complete! To activate this environment, run:"
echo "source venv-py311/bin/activate"
echo ""
echo "To start the development server, run:"
echo "uvicorn app.main:app --reload" 