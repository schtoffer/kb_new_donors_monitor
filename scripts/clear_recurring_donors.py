#!/usr/bin/env python3
"""
Script to clear all data from the recurring_donor table.
This ensures we can test with a clean slate.
"""
import sys
import os

# Add parent directory to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, RecurringDonor

with app.app_context():
    # Delete all records from the recurring_donor table
    num_deleted = db.session.query(RecurringDonor).delete()
    db.session.commit()
    print(f"Cleared {num_deleted} records from the recurring_donor table.")
    
    # Verify the table is empty
    count = db.session.query(RecurringDonor).count()
    print(f"Current record count in recurring_donor table: {count}")

print("Table cleared successfully!")
