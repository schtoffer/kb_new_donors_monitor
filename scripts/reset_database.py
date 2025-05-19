#!/usr/bin/env python3
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db

def reset_database():
    """Drop all tables and recreate them"""
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        print("Database reset complete.")

if __name__ == "__main__":
    reset_database()
