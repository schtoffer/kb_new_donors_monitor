from flask import Flask, render_template, jsonify, request, redirect, url_for
import pandas as pd
import tempfile
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import os
import secrets
import hashlib
import json
import logging
import folium
import sqlite3
import json

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, instance_relative_config=True, static_folder='static', static_url_path='/static')
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
    
    # Fields from Excel (non-personal information only)
    navnenr = db.Column(db.Integer, nullable=True)
    register = db.Column(db.String(50), nullable=True)
    register_1 = db.Column(db.String(255), nullable=True)
    avtalenummer = db.Column(db.String(50), nullable=True)
    postnummer = db.Column(db.String(20), nullable=True)
    poststed = db.Column(db.String(255), nullable=True)
    kommune = db.Column(db.String(255), nullable=True)
    fylke = db.Column(db.String(255), nullable=True)
    landkode = db.Column(db.String(10), nullable=True)
    land = db.Column(db.String(255), nullable=True)
    navnetype = db.Column(db.String(10), nullable=True)
    fodselsaar_startaar = db.Column(db.String(20), nullable=True)
    produktkode = db.Column(db.String(50), nullable=True)
    produkttype = db.Column(db.String(50), nullable=True)
    prosjektnummer = db.Column(db.Integer, nullable=True)
    produkt = db.Column(db.String(255), nullable=True)
    prosjektnavn = db.Column(db.String(255), nullable=True)
    startdato = db.Column(db.String(20), nullable=True)
    betalingsmaate = db.Column(db.String(50), nullable=True)
    girorytme = db.Column(db.Integer, nullable=True)
    betalingsrytme = db.Column(db.String(50), nullable=True)
    belop = db.Column(db.Float, nullable=True)
    aksjonstype = db.Column(db.String(10), nullable=True)
    aksjonstype_beskrivelse = db.Column(db.String(255), nullable=True)
    aksjonsnummer = db.Column(db.String(20), nullable=True)
    aksjonsnavn = db.Column(db.String(255), nullable=True)
    avtaletype = db.Column(db.String(10), nullable=True)
    periode_belop = db.Column(db.Float, nullable=True)
    opprettet_dato = db.Column(db.String(20), nullable=True)
    
    # Legacy fields for backward compatibility
    name_id = db.Column(db.Integer, nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    country_id = db.Column(db.String(10), nullable=True)
    nametype_id = db.Column(db.String(10), nullable=True)
    producttype_id = db.Column(db.String(10), nullable=True)
    project_id = db.Column(db.Integer, nullable=True)
    agreement_number = db.Column(db.String(50), nullable=True)
    amount = db.Column(db.Float, nullable=True)
    interval = db.Column(db.String(20), nullable=True)
    startdate = db.Column(db.Date, nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    campaign_id = db.Column(db.Integer, nullable=True)
    classification_id_success = db.Column(db.String(10), nullable=True)
    
    # No unique constraint needed
    # __table_args__ = (db.UniqueConstraint('name_id', name='unique_name'),)
    
    def to_dict(self):
        # First include the original fields for backward compatibility
        result = {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'campaign_id': self.campaign_id,
            'payment_method': self.payment_method,
            'classification_id_success': self.classification_id_success,
            'name': {
                'name_id': self.name_id,
                'zip': self.zip_code,
                'country_id': self.country_id,
                'nametype_id': self.nametype_id
            },
            'campaign': {
                'aksjonsnummer': self.aksjonsnummer,
                'aksjonsnavn': self.aksjonsnavn
            },
            'agreement': {
                'agreement_number': self.avtalenummer,
                'producttype_id': self.producttype_id,
                'project_id': self.project_id,
                'amount': self.amount,
                'interval': self.interval,
                'startdate': self.startdate.strftime('%d.%m.%Y') if self.startdate else None
            }
        }
        
        # Now add the selected Excel fields
        result['excel_data'] = {
            'navnenr': self.navnenr,
            'register': self.register,
            'register_1': self.register_1,
            'avtalenummer': self.avtalenummer,
            'postnummer': self.postnummer,
            'poststed': self.poststed,
            'kommune': self.kommune,
            'fylke': self.fylke,
            'landkode': self.landkode,
            'land': self.land,
            'navnetype': self.navnetype,
            'fodselsaar_startaar': self.fodselsaar_startaar,
            'produktkode': self.produktkode,
            'produkttype': self.produkttype,
            'prosjektnummer': self.prosjektnummer,
            'produkt': self.produkt,
            'prosjektnavn': self.prosjektnavn,
            'startdato': self.startdato,
            'betalingsmaate': self.betalingsmaate,
            'girorytme': self.girorytme,
            'betalingsrytme': self.betalingsrytme,
            'belop': self.belop,
            'aksjonstype': self.aksjonstype,
            'aksjonstype_beskrivelse': self.aksjonstype_beskrivelse,
            'aksjonsnummer': self.aksjonsnummer,
            'aksjonsnavn': self.aksjonsnavn,
            'avtaletype': self.avtaletype,
            'periode_belop': self.periode_belop,
            'opprettet_dato': self.opprettet_dato
        }
        
        return result

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
    return render_template('report-5.html')

@app.route('/kart')
def kart():
    # Get donor counts by fylke
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fylke, COUNT(*) as count 
        FROM recurring_donor 
        WHERE fylke IS NOT NULL AND fylke != '' 
        GROUP BY fylke 
        ORDER BY count DESC
    """)
    fylke_data = cursor.fetchall()
    conn.close()
    
    # Create a map centered on Norway
    m = folium.Map(location=[65.0, 13.0], zoom_start=4, tiles='CartoDB positron')
    
    # Define mapping for fylke names to match current Norwegian counties (2024)
    fylke_mapping = {
        'Oslo': 'Oslo',
        'Rogaland': 'Rogaland',
        'Møre og Romsdal': 'Møre og Romsdal',
        'Nordland': 'Nordland',
        'Trøndelag': 'Trøndelag',
        'Troms og Finnmark': 'Troms og Finnmark',
        'Vestland': 'Vestland',
        'Agder': 'Agder',
        'Innlandet': 'Innlandet',
        'Vestfold og Telemark': 'Vestfold og Telemark',
        'Viken': 'Viken',
        # Map old county names to new ones
        'Akershus': 'Viken',
        'Buskerud': 'Viken',
        'Østfold': 'Viken',
        'Vestfold': 'Vestfold og Telemark',
        'Telemark': 'Vestfold og Telemark',
        'Oppland': 'Innlandet',
        'Hedmark': 'Innlandet',
        'Aust-Agder': 'Agder',
        'Vest-Agder': 'Agder',
        'Hordaland': 'Vestland',
        'Sogn og Fjordane': 'Vestland',
        'Troms': 'Troms og Finnmark',
        'Finnmark': 'Troms og Finnmark'
    }
    
    # Convert data to a format suitable for Folium, mapping fylke names
    fylke_dict = {}
    for row in fylke_data:
        fylke_name = row[0]
        count = row[1]
        # Map to current county name if available
        if fylke_name in fylke_mapping:
            mapped_name = fylke_mapping[fylke_name]
            if mapped_name in fylke_dict:
                fylke_dict[mapped_name] += count
            else:
                fylke_dict[mapped_name] = count
        else:
            # Keep original name if no mapping exists
            fylke_dict[fylke_name] = count
    
    # Get the minimum and maximum donor counts
    min_donors = min(fylke_dict.values()) if fylke_dict else 0
    max_donors = max(fylke_dict.values()) if fylke_dict else 0
    
    # Create a custom threshold scale for the choropleth map
    # This will use white for 0 and gradually increase to dark orange
    if max_donors > 0:
        # Calculate the step size for the threshold scale
        step = max_donors / 8 if max_donors > 8 else 1
        # Create a threshold scale with white for 0
        threshold_scale = [0, step, step*2, step*3, step*4, step*5, step*6, step*7, max_donors]
    else:
        # If there are no donors, use a default scale
        threshold_scale = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    
    # Create a choropleth map with custom color scheme
    choropleth = folium.Choropleth(
        geo_data='static/data/norway_fylker_kartverket_wgs84.geojson',
        name='choropleth',
        data=fylke_dict,
        key_on='feature.properties.name',
        fill_color='YlOrBr',  # Yellow-Orange-Brown color scheme
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Antall faste givere',
        highlight=True,
        threshold_scale=threshold_scale
    ).add_to(m)
    
    # Create a new GeoJson layer with custom tooltips showing both fylke name and donor count
    # First, prepare the GeoJSON data with donor counts
    import json
    with open('static/data/norway_fylker_kartverket_wgs84.geojson', 'r') as f:
        geojson_data = json.load(f)
    
    # Add donor counts to GeoJSON properties for tooltips
    for feature in geojson_data['features']:
        fylke_name = feature['properties']['name']
        
        # Check if this fylke has donors in our database
        donor_count = 0
        if fylke_name in fylke_dict:
            donor_count = fylke_dict[fylke_name]
        elif fylke_name in fylke_mapping and fylke_mapping[fylke_name] in fylke_dict:
            # Try to find a match using the mapping
            donor_count = fylke_dict[fylke_mapping[fylke_name]]
        else:
            # Try to find a match by checking if this fylke name is a key in the mapping
            for db_name, mapped_name in fylke_mapping.items():
                if mapped_name == fylke_name and db_name in fylke_dict:
                    donor_count += fylke_dict[db_name]
        
        # Add donor count to properties for tooltip display
        feature['properties']['donor_count'] = donor_count
    
    # Save the modified GeoJSON with donor counts
    with open('static/data/norway_fylker_with_counts.geojson', 'w') as f:
        json.dump(geojson_data, f)
    
    # Create a new GeoJson layer with tooltips showing both fylke name and donor count
    tooltip_layer = folium.GeoJson(
        'static/data/norway_fylker_with_counts.geojson',
        name='tooltips',
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'transparent',
            'fillOpacity': 0.0,
            'weight': 0.0
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['name', 'donor_count'],
            aliases=['Fylke:', 'Antall givere:'],
            style=('background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;')
        )
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Create a bar chart for top 5 fylker
    top_fylker = fylke_data[:5]
    
    # Save the map to an HTML file
    map_html = m._repr_html_()
    
    return render_template('kart.html', map_html=map_html, fylke_data=fylke_data, top_fylker=top_fylker)

@app.route('/import')
def import_page():
    return render_template('import.html')

@app.route('/import-excel', methods=['POST'])
def import_excel():
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'message': 'No file part in the request'
        })
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'message': 'No file selected'
        })
    
    # Check if the file is an Excel file
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({
            'success': False,
            'message': 'File must be an Excel file (.xlsx or .xls)'
        })
    
    # Save the file to a temporary location
    temp_dir = tempfile.gettempdir()
    filename = secure_filename(file.filename)
    filepath = os.path.join(temp_dir, filename)
    file.save(filepath)
    
    # Process the Excel file
    try:
        results = process_excel_file(filepath)
        
        # Delete the temporary file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Import completed successfully: {results["added"]} added, {results["updated"]} updated, {results["skipped"]} skipped',
            'results': results
        })
    except Exception as e:
        # Delete the temporary file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        
        app.logger.error(f'Error processing Excel file: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Error processing Excel file: {str(e)}'
        })

def process_excel_file(filepath):
    """
    Process the Excel file and update/insert records in the database
    based on the unique combination of agreement_number and navnenummer.
    
    Returns a dictionary with counts of added, updated, and skipped records.
    """
    # Initialize counters
    added = 0
    updated = 0
    skipped = 0
    details = []
    
    # Read the Excel file
    df = pd.read_excel(filepath)
    
    # Define the allowed columns we want to import
    allowed_columns = [
        'Navnenr', 'Register', 'Register.1', 'Avtalenummer', 'Postnummer', 'Poststed', 
        'Kommune', 'Fylke', 'Landkode', 'Land', 'Navnetype', 'Fødselsår/startår',
        'Produktkode', 'Produkttype', 'Prosjektnummer', 'Produkt', 'Prosjektnavn',
        'Startdato', 'Betalingsmåte', 'Girorytme', 'Betalingsrytme', 'Beløp',
        'Aksjonstype', 'Aksjonstype beskrivelse', 'Aksjonsnummer', 'Aksjonsnavn',
        'Avtaletype', 'Periode beløp', 'Opprettet dato'
    ]
    
    # Filter the DataFrame to only include the allowed columns
    filtered_columns = [col for col in df.columns if col in allowed_columns]
    df_filtered = df[filtered_columns]
    
    # Filter to only include rows where Produkttype is MI or FG
    if 'Produkttype' in df_filtered.columns:
        app.logger.info(f"Before filtering by Produkttype: {len(df_filtered)} records")
        df_filtered = df_filtered[df_filtered['Produkttype'].isin(['MI', 'FG'])]
        app.logger.info(f"After filtering by Produkttype: {len(df_filtered)} records")
    
    # Create a mapping from Excel column names to database field names
    field_mapping = {
        'Navnenr': 'navnenr',
        'Register': 'register',
        'Register.1': 'register_1',
        'Avtalenummer': 'avtalenummer',
        'Postnummer': 'postnummer',
        'Poststed': 'poststed',
        'Kommune': 'kommune',
        'Fylke': 'fylke',
        'Landkode': 'landkode',
        'Land': 'land',
        'Navnetype': 'navnetype',
        'Fødselsår/startår': 'fodselsaar_startaar',
        'Produktkode': 'produktkode',
        'Produkttype': 'produkttype',
        'Prosjektnummer': 'prosjektnummer',
        'Produkt': 'produkt',
        'Prosjektnavn': 'prosjektnavn',
        'Startdato': 'startdato',
        'Betalingsmåte': 'betalingsmaate',
        'Girorytme': 'girorytme',
        'Betalingsrytme': 'betalingsrytme',
        'Beløp': 'belop',
        'Aksjonstype': 'aksjonstype',
        'Aksjonstype beskrivelse': 'aksjonstype_beskrivelse',
        'Aksjonsnummer': 'aksjonsnummer',
        'Aksjonsnavn': 'aksjonsnavn',
        'Avtaletype': 'avtaletype',
        'Periode beløp': 'periode_belop',
        'Opprettet dato': 'opprettet_dato'
    }
    
    # Map legacy fields for backward compatibility
    legacy_field_mapping = {
        'Navnenr': 'name_id',
        'Avtalenummer': 'agreement_number',
        'Postnummer': 'zip_code',
        'Landkode': 'country_id',
        'Navnetype': 'nametype_id',
        'Produkttype': 'producttype_id',
        'Prosjektnummer': 'project_id',
        'Beløp': 'amount',
        'Betalingsrytme': 'interval',
        'Startdato': 'startdate',
        'Betalingsmåte': 'payment_method'
    }
    
    # Convert filtered DataFrame to list of dictionaries
    records = df_filtered.to_dict('records')
    
    with app.app_context():
        for record in records:
            # Create a dictionary with only the allowed fields from Excel
            donor_data = {}
            
            # Map allowed Excel columns to their corresponding database fields
            for column, value in record.items():
                if column in field_mapping:
                    field_name = field_mapping[column]
                    
                    # Handle NaN values
                    if pd.isna(value):
                        donor_data[field_name] = None
                    # Handle numeric fields
                    elif field_name in ['navnenr', 'prosjektnummer', 'girorytme']:
                        try:
                            donor_data[field_name] = int(value) if not pd.isna(value) else None
                        except (ValueError, TypeError):
                            donor_data[field_name] = None
                    # Handle float fields
                    elif field_name in ['belop', 'periode_belop']:
                        try:
                            donor_data[field_name] = float(value) if not pd.isna(value) else None
                        except (ValueError, TypeError):
                            donor_data[field_name] = None
                    # Handle all other fields as strings
                    else:
                        donor_data[field_name] = str(value) if not pd.isna(value) else None
            
            # Also populate legacy fields for backward compatibility
            for column, legacy_field in legacy_field_mapping.items():
                if column in record:
                    value = record[column]
                    
                    # Special handling for certain legacy fields
                    if legacy_field == 'startdate' and not pd.isna(value):
                        try:
                            # Try to parse the date
                            date_str = str(value)
                            if '.' in date_str:
                                donor_data[legacy_field] = datetime.strptime(date_str, '%d.%m.%Y').date()
                                # Store the date only in the date object format, not as a string
                                if 'startdato' in donor_data:
                                    donor_data.pop('startdato')
                            else:
                                donor_data[legacy_field] = datetime.strptime(date_str, '%Y-%m-%d').date()
                        except (ValueError, TypeError):
                            donor_data[legacy_field] = None
                    elif legacy_field in ['name_id', 'project_id'] and not pd.isna(value):
                        try:
                            donor_data[legacy_field] = int(value)
                        except (ValueError, TypeError):
                            donor_data[legacy_field] = None
                    elif legacy_field == 'amount' and not pd.isna(value):
                        try:
                            donor_data[legacy_field] = float(value)
                        except (ValueError, TypeError):
                            donor_data[legacy_field] = None
                    elif not pd.isna(value):
                        donor_data[legacy_field] = str(value)
            
            # Set default values for campaign_id and classification_id_success if not present
            if 'campaign_id' not in donor_data or donor_data['campaign_id'] is None:
                donor_data['campaign_id'] = random.randint(1, 10)
            
            if 'classification_id_success' not in donor_data or donor_data['classification_id_success'] is None:
                donor_data['classification_id_success'] = 'S1'
            
            # Only process the donor if Produkttype is MI or FG
            produkttype = donor_data.get('produkttype')
            if produkttype in ['MI', 'FG']:
                try:
                    # Check if we have both agreement_number and navnenr/name_id
                    agreement_number = donor_data.get('agreement_number')
                    name_id = donor_data.get('name_id')
                    
                    if agreement_number and name_id:
                        # Check if a record with the same agreement_number and name_id exists
                        existing_donor = RecurringDonor.query.filter_by(
                            agreement_number=agreement_number,
                            name_id=name_id
                        ).first()
                        
                        if existing_donor:
                            # Update existing record
                            for key, value in donor_data.items():
                                setattr(existing_donor, key, value)
                            updated += 1
                            details.append(f"Updated donor with agreement_number={agreement_number}, name_id={name_id}")
                        else:
                            # Add new record
                            new_donor = RecurringDonor(**donor_data)
                            db.session.add(new_donor)
                            added += 1
                            details.append(f"Added new donor with agreement_number={agreement_number}, name_id={name_id}")
                    else:
                        # Skip records without both agreement_number and name_id
                        skipped += 1
                        details.append(f"Skipped record: Missing agreement_number or name_id")
                    
                    # Commit every 100 records to avoid large transactions
                    if (added + updated) % 100 == 0:
                        db.session.commit()
                        app.logger.info(f"Committed {added + updated} records so far...")
                except Exception as e:
                    app.logger.error(f"Error processing donor: {str(e)}")
                    app.logger.error(f"Problematic data: {donor_data}")
                    db.session.rollback()
                    skipped += 1
                    details.append(f"Error processing record: {str(e)}")
            else:
                skipped += 1
                details.append(f"Skipped record with Produkttype: {produkttype if produkttype else 'Missing'}")
        
        # Final commit for any remaining records
        try:
            db.session.commit()
            app.logger.info(f"Import completed: {added} added, {updated} updated, {skipped} skipped")
        except Exception as e:
            app.logger.error(f"Error during final commit: {str(e)}")
            db.session.rollback()
            details.append(f"Error during final commit: {str(e)}")
    
    # Return the results
    return {
        "added": added,
        "updated": updated,
        "skipped": skipped,
        "details": details[:20]  # Limit details to avoid too large response
    }


@app.route('/report-5')
def report_5():
    return render_template('report-5.html')

@app.route('/recurring-donors')
def recurring_donors():
    # Get all recurring donors from the database
    donors = RecurringDonor.query.all()
    
    # Prepare data for the template
    donor_data = []
    total_amount = 0
    unique_products = set()
    unique_payment_methods = set()
    
    for donor in donors:
        donor_info = {
            'name_id': donor.name_id,
            'payment_method': donor.payment_method,
            'amount': donor.amount if donor.amount is not None else 0,
            'interval': donor.interval,
            'startdate': donor.startdate.strftime('%d.%m.%Y') if donor.startdate else '',
            'producttype_id': donor.producttype_id,
            'agreement_number': donor.agreement_number
        }
        donor_data.append(donor_info)
        total_amount += donor.amount if donor.amount is not None else 0
        
        # Add product to the unique products set
        if donor.producttype_id:
            unique_products.add(donor.producttype_id)
            
        # Add payment method to the unique payment methods set
        if donor.payment_method:
            unique_payment_methods.add(donor.payment_method)
    
    # Format the total amount with thousand separator
    formatted_total = '{:,.0f}'.format(total_amount).replace(',', ' ')
    
    # Convert the sets to sorted lists for the template
    product_list = sorted(list(unique_products))
    payment_method_list = sorted(list(unique_payment_methods))
    
    return render_template('recurring_donors.html', 
                           donors=donor_data, 
                           total_donors=len(donor_data), 
                           total_amount=formatted_total,
                           products=product_list,
                           payment_methods=payment_method_list)

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
    required_agreement = ['producttype_id', 'project_id', 'amount', 'interval', 'startdate']
    
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
        # Check if a record with the same name_id already exists
        # Ensure name_id is treated as an integer
        name_id = int(data['name']['name_id'])
        existing_record = RecurringDonor.query.filter_by(
            name_id=name_id
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
                producttype_id=data['agreement']['producttype_id'],
                project_id=data['agreement']['project_id'],
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
    Also includes data for the last 14 days for the graph
    """
    today = datetime.now().date()
    
    # Instead of using today's date, find the most recent date with donors
    # First check the last 7 days to find a date with donors
    recent_donors = []
    recent_date = None
    recent_date_str = None
    
    # Try to find donors from the last 7 days
    for i in range(7):
        check_date = today - timedelta(days=i)
        check_date_str = check_date.strftime('%d.%m.%Y')
        
        # Check both date formats
        date_donors = RecurringDonor.query.filter_by(startdate=check_date).all()
        string_donors = RecurringDonor.query.filter_by(startdato=check_date_str).all()
        
        # Combine donors from both date formats
        combined_donors = list(set(date_donors + string_donors))
        
        if combined_donors:
            recent_donors = combined_donors
            recent_date = check_date
            recent_date_str = check_date_str
            print(f"Found {len(recent_donors)} donors for date {recent_date_str}")
            break
    
    # If no donors found in the last 7 days, use today's date but with empty donors list
    if not recent_donors:
        recent_date = today
        recent_date_str = today.strftime('%d.%m.%Y')
        recent_donors = []
        print(f"No donors found in the last 7 days. Using today's date with 0 donors.")
    
    # Use the recent donors as our "today's" donors
    new_donors_today = recent_donors
    
    # Filter to only include MI and FG product types
    new_donors_today = [donor for donor in new_donors_today 
                        if hasattr(donor, 'produkttype') and donor.produkttype in ['MI', 'FG'] or 
                           hasattr(donor, 'producttype_id') and donor.producttype_id in ['MI', 'FG']]
    
    # Calculate total value (no longer multiplying by 12) - ensure amount is available
    yearly_value = sum(donor.amount for donor in new_donors_today if donor.amount is not None)
    
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
    # Use the recent date as reference
    if recent_date:
        reference_date = recent_date
    else:
        reference_date = today
        
    thirty_days_ago = reference_date - timedelta(days=30)
    last_30_days_counts = []
    
    for i in range(30):
        date = reference_date - timedelta(days=i + 1)  # Skip reference date
        date_str = date.strftime('%d.%m.%Y')
        
        # Count donors with matching date field
        date_count = RecurringDonor.query.filter_by(startdate=date).count()
        
        # Count donors with matching string date field
        string_count = RecurringDonor.query.filter_by(startdato=date_str).count()
        
        # Add the total count for this date
        total_count = date_count + string_count
        last_30_days_counts.append(total_count)
    
    average_new_donors = round(sum(last_30_days_counts) / len(last_30_days_counts)) if last_30_days_counts else 0
    
    # Get historical data for the last 14 days
    # Use today's date as reference for the graph
    reference_date = today
    print(f"Debug - Today's date: {today}, Reference date for graph: {reference_date}")
        
    historical_data = []
    print(f"Debug - Date range for graph:")
    for i in range(14, -1, -1):
        date = reference_date - timedelta(days=i)
        date_str = date.strftime('%d.%m.%Y')
        print(f"Debug - Processing date: {date_str} ({i} days before reference date)")
        
        # Get donors with matching date field
        date_donors = RecurringDonor.query.filter_by(startdate=date).all()
        
        # Get donors with matching string date field
        string_donors = RecurringDonor.query.filter_by(startdato=date_str).all()
        
        # Combine donors from both date formats and remove duplicates based on name_id
        all_donors = date_donors + string_donors
        
        # Create a dictionary with name_id as key to remove duplicates
        unique_donors_dict = {}
        for donor in all_donors:
            if donor.name_id not in unique_donors_dict:
                unique_donors_dict[donor.name_id] = donor
        
        # Convert back to list
        donors_on_date = list(unique_donors_dict.values())
        
        # Debug output for May 17, 2025
        if date_str == '17.05.2025':
            print(f"Debug - May 17, 2025 - Date donors: {len(date_donors)}, String donors: {len(string_donors)}, Raw combined: {len(all_donors)}, After deduplication: {len(donors_on_date)}")
            print(f"Debug - May 17, 2025 - Date format: {date}, String format: {date_str}")
        
        # Filter to only include MI and FG product types
        donors_on_date = [donor for donor in donors_on_date 
                          if hasattr(donor, 'produkttype') and donor.produkttype in ['MI', 'FG'] or 
                             hasattr(donor, 'producttype_id') and donor.producttype_id in ['MI', 'FG']]
        
        # More debug for May 17, 2025
        if date_str == '17.05.2025':
            print(f"Debug - May 17, 2025 - After filtering: {len(donors_on_date)}")
            # Check for duplicates in another way
            name_ids = [donor.name_id for donor in donors_on_date if donor.name_id is not None]
            print(f"Debug - May 17, 2025 - Unique name_ids: {len(set(name_ids))}, Total name_ids: {len(name_ids)}")
        
        # Calculate daily value - ensure amount is available
        daily_value = sum(donor.amount for donor in donors_on_date if donor.amount is not None)
        
        # Format date as DD.MM
        formatted_date = date.strftime('%d.%m')
        
        historical_data.append({
            'date': formatted_date,
            'count': len(donors_on_date),
            'value': daily_value
        })
    
    # Reverse the data so it's in chronological order (oldest to newest)
    historical_data.reverse()
    
    return jsonify({
        'count': len(new_donors_today),
        'yearly_value': yearly_value,
        'average_new_donors_last_30_days': average_new_donors,
        'payment_methods': payment_methods,
        'products': products,
        'last_14_days': historical_data
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
