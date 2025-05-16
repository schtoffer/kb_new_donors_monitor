#!/bin/bash
cd ~/kb_fg_monitor
# Check if virtual environment exists
if [ -d "venv" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate
else
  echo "Creating virtual environment..."
  python3 -m venv venv
  source venv/bin/activate
  echo "Installing dependencies..."
  pip install flask flask-sqlalchemy
fi

# Run the app
echo "Starting Flask app..."
python app.py > ~/flask.log 2>&1
