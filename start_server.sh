#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Stop any running instances
echo "Stopping running servers..."
pkill -f "uvicorn ges_neu_api" || true

# Set up environment
export PYTHONPATH=$(pwd):$PYTHONPATH

# Install the package in development mode
echo "Installing package in development mode..."
pip install -e .

# Start the server
echo "Starting server at http://localhost:8001"

# Run uvicorn with the module path
uvicorn ges_neu_api.main:app \
    --host "0.0.0.0" \
    --port 8001 \
    --reload \
    --log-level debug

echo ""
echo "If you encounter any errors, please verify that:"
echo "1. The virtual environment is activated (source .venv/bin/activate)"
echo "2. Dependencies are installed (pip install -e .)"
echo "3. The database is running"
