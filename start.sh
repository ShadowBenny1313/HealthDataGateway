#!/bin/bash

# Start HealthData Gateway service
echo "Starting HealthData Gateway..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Make sure dependencies are installed
pip install -r requirements.txt

# Start the server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
