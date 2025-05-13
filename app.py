from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///donors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

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

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/service')
def service():
    # Get the device's IP address
    import socket
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return render_template('service.html', ip_address=ip_address)

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
    app.run(debug=True)
