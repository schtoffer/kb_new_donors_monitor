#!/usr/bin/env python3
"""
Script to populate the recurring_donor table with sample data.
This script first clears the table and then adds sample data from 01.01.2025 onwards.
"""
import sys
import os

# Add parent directory to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, RecurringDonor
import random
from datetime import datetime, timedelta
import string

# Payment method options
PAYMENT_METHODS = ['vippsrecurring', 'striprecurring']

# Product type options
PRODUCT_TYPES = ['FG', 'MI']

# Intervals
INTERVALS = ['Monthly', 'Quarterly', 'Yearly']

# Country codes
COUNTRIES = ['NO', 'SE', 'DK', 'FI']

# Name types
NAME_TYPES = ['P', 'D', 'C']

def generate_agreement_number(length=6):
    """Generate a random agreement number"""
    return ''.join(random.choices(string.digits, k=length))

def generate_random_donor(start_date):
    """Generate random donor data"""
    return {
        'name_id': random.randint(1000, 9999),
        'payment_method': random.choice(PAYMENT_METHODS),
        'agreement_number': generate_agreement_number(),
        'amount': random.randint(40, 240),
        'interval': random.choice(INTERVALS),
        'startdate': start_date,
        'producttype_id': random.choice(PRODUCT_TYPES),
        'productvariant_id': None,
        'project_id': random.randint(0, 10),
        'campaign_id': random.randint(100, 200),
        'classification_id_success': 'BG',
        'zip_code': ''.join(random.choices(string.digits, k=4)),
        'country_id': random.choice(COUNTRIES),
        'nametype_id': random.choice(NAME_TYPES)
    }

def populate_db():
    with app.app_context():
        # Clear the table first
        print("Clearing existing data...")
        db.session.query(RecurringDonor).delete()
        db.session.commit()
        
        # Start date
        start_date = datetime(2025, 1, 1)
        end_date = datetime.now()
        
        # Track total donors added
        total_donors = 0
        
        # Loop through each day
        current_date = start_date
        while current_date <= end_date:
            # Generate between 5 and 20 records per day
            num_records = random.randint(5, 20)
            
            print(f"Adding {num_records} records for {current_date.strftime('%Y-%m-%d')}...")
            
            for _ in range(num_records):
                donor_data = generate_random_donor(current_date)
                
                # Create new donor record
                donor = RecurringDonor(
                    name_id=donor_data['name_id'],
                    payment_method=donor_data['payment_method'],
                    agreement_number=donor_data['agreement_number'],
                    amount=donor_data['amount'],
                    interval=donor_data['interval'],
                    startdate=donor_data['startdate'],
                    producttype_id=donor_data['producttype_id'],
                    productvariant_id=donor_data['productvariant_id'],
                    project_id=donor_data['project_id'],
                    campaign_id=donor_data['campaign_id'],
                    classification_id_success=donor_data['classification_id_success'],
                    zip_code=donor_data['zip_code'],
                    country_id=donor_data['country_id'],
                    nametype_id=donor_data['nametype_id']
                )
                
                db.session.add(donor)
                total_donors += 1
            
            # Move to next day
            current_date += timedelta(days=1)
        
        # Commit all changes
        db.session.commit()
        print(f"Successfully added {total_donors} sample donors from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    populate_db()
    print("Database population completed successfully!")
