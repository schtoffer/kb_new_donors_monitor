from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import os
import secrets
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///donors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

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
    return render_template('report-3.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/alternative-2')
def alternative_2():
    return render_template('report-2.html')

@app.route('/alternative-3')
def alternative_3():
    return render_template('report-3.html')

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
    port = request.environ.get('SERVER_PORT', 5001)
    
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Get port from environment variable or use default 5001
    port = int(os.environ.get('PORT', 5001))
    # Use the specific IP address or 0.0.0.0 to listen on all interfaces
    app.run(host='0.0.0.0', port=port, debug=True)
