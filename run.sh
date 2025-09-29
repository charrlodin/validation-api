#!/bin/bash

echo "Starting Email & IP Validation API..."
echo "======================================"
echo ""
echo "Setting up virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
fi

source venv/bin/activate
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Starting API server..."
echo "Access the API at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
