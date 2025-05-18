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
fi

# Always install/update dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Run the app
echo "Starting Flask app..."
python app.py > ~/flask.log 2>&1
