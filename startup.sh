#!/bin/bash

# Log startup information
echo "Starting KB FG Monitor application..."

# Activate virtual environment (Azure creates this automatically)
if [ -d "antenv" ]; then
    echo "Activating virtual environment..."
    source antenv/bin/activate
fi

# Start the application with gunicorn
echo "Starting gunicorn server..."
gunicorn --bind=0.0.0.0:8000 app:app --timeout 600
