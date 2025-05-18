from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import os
import secrets
import hashlib
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, instance_relative_config=True)
# Make sure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)
# Use absolute path for SQLite database
db_path = os.path.join(app.instance_path, 'donors.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Log startup information
app.logger.info('Starting KB FG Monitor application')
app.logger.info(f'Current directory: {os.getcwd()}')
app.logger.info(f'Files in current directory: {os.listdir(".")}')
app.logger.info(f'Files in instance directory: {os.listdir("instance") if os.path.exists("instance") else "No instance directory"}')

# Disable caching
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

template_dir = os.path.abspath('templates')
app.template_folder = template_dir
db = SQLAlchemy(app)

class DonorStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    n_new_donors = db.Column(db.Integer, nullable=False)
    yearly_sum_new_donors = db.Column(db.Float, nullable=False)
    n_total_new_donors = db.Column(db.Integer, nullable=False)
    yearly_sum_all_donors = db.Column(db.Float, nullable=False)

class RecurringDonor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Top level fields
    campaign_id = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    classification_id_success = db.Column(db.String(10), nullable=False)
    
    # Name fields
    name_id = db.Column(db.Integer, nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    country_id = db.Column(db.String(10), nullable=False)
    nametype_id = db.Column(db.String(10), nullable=False)
    
    # Agreement fields
    agreement_number = db.Column(db.String(50), nullable=False)
    producttype_id = db.Column(db.String(10), nullable=False)
    project_id = db.Column(db.Integer, nullable=False)
    productvariant_id = db.Column(db.Integer, nullable=True)
    amount = db.Column(db.Float, nullable=False)
    interval = db.Column(db.String(20), nullable=False)
    startdate = db.Column(db.Date, nullable=False)
    
    # Define a unique constraint on name_id and agreement_number
    __table_args__ = (db.UniqueConstraint('name_id', 'agreement_number', name='unique_name_agreement'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'campaign_id': self.campaign_id,
            'payment_method': self.payment_method,
            'classification_id_success': self.classification_id_success,
            'name': {
                'name_id': self.name_id,  # Already an integer in the database
                'zip': self.zip_code,
                'country_id': self.country_id,
                'nametype_id': self.nametype_id
            },
            'agreement': {
                'agreement_number': self.agreement_number,
                'producttype_id': self.producttype_id,
                'project_id': self.project_id,
                'productvariant_id': self.productvariant_id,
                'amount': self.amount,
                'interval': self.interval,
                'startdate': self.startdate.strftime('%d.%m.%Y') if self.startdate else None
            }
        }

    @classmethod
    def update_or_create(cls, date, n_new_donors, yearly_sum_new_donors, n_total_new_donors, yearly_sum_all_donors):
        """
        Update existing record or create new one if date doesn't exist
        """
        record = cls.query.filter_by(date=date).first()
        if record:
            record.n_new_donors = n_new_donors
            record.yearly_sum_new_donors = yearly_sum_new_donors
            record.n_total_new_donors = n_total_new_donors
            record.yearly_sum_all_donors = yearly_sum_all_donors
        else:
            record = cls(
                date=date,
                n_new_donors=n_new_donors,
                yearly_sum_new_donors=yearly_sum_new_donors,
                n_total_new_donors=n_total_new_donors,
                yearly_sum_all_donors=yearly_sum_all_donors
            )
            db.session.add(record)
        db.session.commit()
        return record

# API key for vendor authentication - in production, store this securely
# Generate a random API key for initial setup
API_KEY = os.environ.get('VENDOR_API_KEY', 'test_api_key_123')

@app.route('/')
def index():
    return render_template('report-4.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/alternative-2')
def alternative_2():
    return render_template('report-2.html')

@app.route('/alternative-3')
def alternative_3():
    return render_template('report-3.html')

@app.route('/report-4')
def report_4():
    return render_template('report-4.html')

@app.route('/recurring-donors')
def recurring_donors():
    # Get all recurring donors from the database
    donors = RecurringDonor.query.all()
    
    # Prepare data for the template
    donor_data = []
    total_amount = 0
    unique_products = set()
    
    for donor in donors:
        donor_info = {
            'name_id': donor.name_id,
            'payment_method': donor.payment_method,
            'agreement_number': donor.agreement_number,
            'amount': donor.amount,
            'interval': donor.interval,
            'startdate': donor.startdate.strftime('%d.%m.%Y') if donor.startdate else '',
            'producttype_id': donor.producttype_id
        }
        donor_data.append(donor_info)
        total_amount += donor.amount
        
        # Add product to the unique products set
        if donor.producttype_id:
            unique_products.add(donor.producttype_id)
    
    # Format the total amount with thousand separator
    formatted_total = '{:,.0f}'.format(total_amount).replace(',', ' ')
    
    # Convert the set to a sorted list for the template
    product_list = sorted(list(unique_products))
    
    return render_template('recurring_donors.html', 
                           donors=donor_data, 
                           total_donors=len(donor_data), 
                           total_amount=formatted_total,
                           products=product_list)

@app.route('/service')
def service():
    # Get the device's IP address
    import socket
    import subprocess
    
    try:
        # Try to get the IP address using the hostname command
        ip_address = subprocess.check_output(['hostname', '-I']).decode('utf-8').strip().split()[0]
    except:
        try:
            # Fallback method 1: Try to get IP by creating a socket connection
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
        except:
            # Fallback method 2: Use hostname
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
    
    # Get the port the server is running on
    port = request.environ.get('SERVER_PORT', 5000)
    
    # Format the IP address as a URL with the current port
    url = f"http://{ip_address}:{port}"
    
    return render_template('service.html', ip_address=url)

@app.route('/api/today')
def get_today():
    today = datetime.now().date()
    record = DonorStats.query.filter_by(date=today).first()
    
    # Calculate the average of n_new_donors for the last 30 days
    thirty_days_ago = today - timedelta(days=30)
    last_30_days_records = DonorStats.query.filter(DonorStats.date >= thirty_days_ago).all()
    
    average_n_new_donors_last_30_days = 0
    if last_30_days_records:
        average_n_new_donors_last_30_days = round(sum(r.n_new_donors for r in last_30_days_records) / len(last_30_days_records))
    
    if record:
        return jsonify({
            'n_new_donors': record.n_new_donors,
            'yearly_sum_new_donors': record.yearly_sum_new_donors,
            'average_n_new_donors_last_30_days': average_n_new_donors_last_30_days
        })
    return jsonify({'error': 'No data for today'}), 404

@app.route('/api/donor-stats', methods=['POST'])
def update_donor_stats():
    # Authenticate the request
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header.split(' ')[1]
    if not secrets.compare_digest(token, API_KEY):
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Validate the request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['date', 'n_new_donors', 'yearly_sum_new_donors', 'n_total_new_donors', 'yearly_sum_all_donors']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        # Parse the date
        if isinstance(data['date'], str):
            date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        else:
            return jsonify({'error': 'Date must be in YYYY-MM-DD format'}), 400
            
        # Update or create the record
        DonorStats.update_or_create(
            date=date,
            n_new_donors=int(data['n_new_donors']),
            yearly_sum_new_donors=float(data['yearly_sum_new_donors']),
            n_total_new_donors=int(data['n_total_new_donors']),
            yearly_sum_all_donors=float(data['yearly_sum_all_donors'])
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Donor statistics updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/populate')
def populate_db():
    start_date = datetime(2025, 1, 1)
    end_date = datetime.now()
    
    current_date = start_date
    while current_date <= end_date:
        n_new_donors = random.randint(18, 47)
        yearly_sum_new_donors = n_new_donors * 720
        n_total_new_donors = 48000
        yearly_sum_all_donors = 67680000
        
        DonorStats.update_or_create(
            date=current_date.date(),
            n_new_donors=n_new_donors,
            yearly_sum_new_donors=yearly_sum_new_donors,
            n_total_new_donors=n_total_new_donors,
            yearly_sum_all_donors=yearly_sum_all_donors
        )
        
        current_date += timedelta(days=1)
    
    return 'Database populated successfully!'

@app.route('/api/new-recurring-donor', methods=['POST'])
def new_recurring_donor():
    # Authenticate the request
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header.split(' ')[1]
    if not secrets.compare_digest(token, API_KEY):
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Validate the request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Check required fields
    required_top_level = ['campaign_id', 'payment_method', 'classification_id_success', 'name', 'agreement']
    required_name = ['name_id', 'zip', 'country_id', 'nametype_id']
    required_agreement = ['agreement_number', 'producttype_id', 'project_id', 'amount', 'interval', 'startdate']
    
    # Validate top-level fields
    for field in required_top_level:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate name fields
    for field in required_name:
        if field not in data['name']:
            return jsonify({'error': f'Missing required name field: {field}'}), 400
    
    # Validate agreement fields
    for field in required_agreement:
        if field not in data['agreement']:
            return jsonify({'error': f'Missing required agreement field: {field}'}), 400
    
    try:
        # Check if a record with the same name_id and agreement_number already exists
        # Ensure name_id is treated as an integer
        name_id = int(data['name']['name_id'])
        existing_record = RecurringDonor.query.filter_by(
            name_id=name_id,
            agreement_number=data['agreement']['agreement_number']
        ).first()
        
        if existing_record:
            # Update the existing record
            existing_record.campaign_id = data['campaign_id']
            existing_record.payment_method = data['payment_method']
            existing_record.classification_id_success = data['classification_id_success']
            
            # Update name information
            existing_record.zip_code = data['name']['zip']
            existing_record.country_id = data['name']['country_id']
            existing_record.nametype_id = data['name']['nametype_id']
            
            # Update agreement information
            existing_record.producttype_id = data['agreement']['producttype_id']
            existing_record.project_id = data['agreement']['project_id']
            existing_record.productvariant_id = data['agreement'].get('productvariant_id')
            existing_record.amount = data['agreement']['amount']
            existing_record.interval = data['agreement']['interval']
            # Parse startdate from string to date object
            try:
                # Try to parse date in DD.MM.YYYY format
                existing_record.startdate = datetime.strptime(data['agreement']['startdate'], '%d.%m.%Y').date()
            except ValueError:
                try:
                    # Fallback to YYYY-MM-DD format
                    existing_record.startdate = datetime.strptime(data['agreement']['startdate'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid startdate format. Use DD.MM.YYYY or YYYY-MM-DD'}), 400
            
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Recurring donor updated successfully',
                'donor': existing_record.to_dict()
            }), 200
        else:
            # Create a new record
            new_donor = RecurringDonor(
                campaign_id=data['campaign_id'],
                payment_method=data['payment_method'],
                classification_id_success=data['classification_id_success'],
                
                # Name information
                name_id=int(data['name']['name_id']),
                zip_code=data['name']['zip'],
                country_id=data['name']['country_id'],
                nametype_id=data['name']['nametype_id'],
                
                # Agreement information
                agreement_number=data['agreement']['agreement_number'],
                producttype_id=data['agreement']['producttype_id'],
                project_id=data['agreement']['project_id'],
                productvariant_id=data['agreement'].get('productvariant_id'),
                amount=data['agreement']['amount'],
                interval=data['agreement']['interval'],
                # Parse startdate from string to date object
                startdate=parse_date(data['agreement']['startdate'])
            )
            
            db.session.add(new_donor)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Recurring donor created successfully',
                'donor': new_donor.to_dict()
            }), 201
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def parse_date(date_string):
    """Parse a date string in either DD.MM.YYYY or YYYY-MM-DD format"""
    try:
        # Try DD.MM.YYYY format first (as in the example)
        return datetime.strptime(date_string, '%d.%m.%Y').date()
    except ValueError:
        try:
            # Fallback to YYYY-MM-DD format
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            # If both fail, raise an exception
            raise ValueError(f"Invalid date format: {date_string}. Use DD.MM.YYYY or YYYY-MM-DD")

@app.route('/api/recurring-donors', methods=['GET'])
def get_recurring_donors():
    """Get all recurring donors or filter by name_id"""
    name_id = request.args.get('name_id')
    
    try:
        if name_id:
            try:
                # Convert name_id to integer for filtering
                name_id_int = int(name_id)
                donors = RecurringDonor.query.filter_by(name_id=name_id_int).all()
            except ValueError:
                # If name_id can't be converted to int, return empty result
                donors = []
        else:
            donors = RecurringDonor.query.all()
        
        return jsonify({
            'status': 'success',
            'count': len(donors),
            'donors': [donor.to_dict() for donor in donors]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/new-donors-today')
def get_new_donors_today():
    """
    Get statistics about new donors that started today based on the startdate column
    """
    today = datetime.now().date()
    
    # Find all donors that started today
    new_donors_today = RecurringDonor.query.filter_by(startdate=today).all()
    
    # Calculate yearly value (amount * 12 for each donor)
    yearly_value = sum(donor.amount * 12 for donor in new_donors_today)
    
    # Get payment method breakdown
    payment_methods = {}
    for donor in new_donors_today:
        method = donor.payment_method
        payment_methods[method] = payment_methods.get(method, 0) + 1
    
    # Get product breakdown
    products = {}
    for donor in new_donors_today:
        product = donor.producttype_id
        products[product] = products.get(product, 0) + 1
    
    # Calculate the average of new donors for the last 30 days
    thirty_days_ago = today - timedelta(days=30)
    last_30_days_counts = []
    
    for i in range(30):
        date = today - timedelta(days=i + 1)  # Skip today
        count = RecurringDonor.query.filter_by(startdate=date).count()
        last_30_days_counts.append(count)
    
    average_new_donors = round(sum(last_30_days_counts) / len(last_30_days_counts)) if last_30_days_counts else 0
    
    return jsonify({
        'count': len(new_donors_today),
        'yearly_value': yearly_value,
        'average_new_donors_last_30_days': average_new_donors,
        'payment_methods': payment_methods,
        'products': products
    })

# Create database tables if they don't exist
with app.app_context():
    try:
        # Ensure the instance directory exists and has proper permissions
        os.makedirs(app.instance_path, exist_ok=True)
        # Create database tables
        db.create_all()
        app.logger.info(f'Database tables created successfully at {db_path}')
    except Exception as e:
        app.logger.error(f'Error creating database tables: {e}')

if __name__ == '__main__':
    # Get port from environment variable or use default 5000
    port = int(os.environ.get('PORT', 8000))
    # Use the specific IP address or 0.0.0.0 to listen on all interfaces
    app.run(host='0.0.0.0', port=port, debug=True)
