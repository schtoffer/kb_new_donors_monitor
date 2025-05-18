from app import app, db, RecurringDonor
from datetime import datetime, timedelta
import random

# Sample data for generating realistic test data
payment_methods = ['Avtalegiro', 'Vipps', 'Kredittkort', 'PayPal']
product_types = ['Fadder', 'Generell', 'Nødhjelp', 'Barn i Norge', 'Utdanning']
intervals = ['monthly', 'quarterly', 'yearly']
amounts = [100, 150, 200, 250, 300, 350, 400, 500, 750, 1000]

def create_donor(startdate, payment_method=None, product_type=None, amount=None):
    """Create a new recurring donor with the given startdate"""
    if payment_method is None:
        payment_method = random.choice(payment_methods)
    if product_type is None:
        product_type = random.choice(product_types)
    if amount is None:
        amount = random.choice(amounts)
        
    # Generate a unique name_id and agreement_number
    name_id = random.randint(10000, 99999)
    agreement_number = f"AG{random.randint(100000, 999999)}"
    
    # Create a new donor
    donor = RecurringDonor(
        campaign_id=random.randint(1, 10),
        payment_method=payment_method,
        classification_id_success="S1",
        name_id=name_id,
        zip_code=f"{random.randint(1000, 9999)}",
        country_id="NO",
        nametype_id="P",
        agreement_number=agreement_number,
        producttype_id=product_type,
        project_id=random.randint(1, 5),
        productvariant_id=random.randint(1, 3),
        amount=amount,
        interval=random.choice(intervals),
        startdate=startdate
    )
    
    return donor

def populate_database():
    """Populate the database with test data"""
    with app.app_context():
        # Clear existing data
        db.session.query(RecurringDonor).delete()
        db.session.commit()
        
        # Get today's date
        today = datetime.now().date()
        
        # Create donors with today's date (new donors)
        new_donors_count = random.randint(15, 30)
        print(f"Creating {new_donors_count} new donors for today ({today})")
        
        # Ensure we have a mix of payment methods and product types
        for i in range(new_donors_count):
            payment_method = payment_methods[i % len(payment_methods)]
            product_type = product_types[i % len(product_types)]
            amount = amounts[i % len(amounts)]
            
            donor = create_donor(today, payment_method, product_type, amount)
            db.session.add(donor)
        
        # Create donors for the past 30 days (for historical data)
        for days_ago in range(1, 31):
            date = today - timedelta(days=days_ago)
            donors_count = random.randint(5, 25)  # Random number of donors per day
            
            print(f"Creating {donors_count} donors for {date}")
            
            for _ in range(donors_count):
                donor = create_donor(date)
                db.session.add(donor)
        
        # Commit all changes
        db.session.commit()
        
        # Print summary
        total_donors = RecurringDonor.query.count()
        today_donors = RecurringDonor.query.filter_by(startdate=today).count()
        
        print(f"\nDatabase populated with {total_donors} donors total")
        print(f"{today_donors} donors with today's date ({today})")

if __name__ == "__main__":
    populate_database()
