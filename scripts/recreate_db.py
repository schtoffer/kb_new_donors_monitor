#!/usr/bin/env python3
"""
Script to recreate the database with the correct schema.
This ensures the startdate field is properly defined as a DATE type.
"""
import sys
import os

# Add parent directory to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
import os

# Make sure the instance directory exists
os.makedirs('instance', exist_ok=True)

# Path to the database file
db_path = os.path.join('instance', 'donors.db')

# Remove the database file if it exists
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Removed existing database: {db_path}")

# Create the database with the new schema
with app.app_context():
    db.create_all()
    print(f"Created new database with updated schema: {db_path}")

print("Database recreation completed successfully!")
