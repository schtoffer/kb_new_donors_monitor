#!/usr/bin/env python3
import os
import sys
import pandas as pd
from datetime import datetime
import random
import argparse

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, RecurringDonor
from datetime import datetime

def clear_database():
    """Clear all data from the RecurringDonor table"""
    with app.app_context():
        try:
            # Get the count of records before deletion
            count_before = RecurringDonor.query.count()
            print(f"Found {count_before} records in the database.")
            
            # Delete all records
            RecurringDonor.query.delete()
            db.session.commit()
            
            # Verify deletion
            count_after = RecurringDonor.query.count()
            print(f"Database cleared. {count_before - count_after} records deleted.")
            
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            db.session.rollback()
            return False

def reset_database():
    """Drop all tables and recreate them"""
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        print("Database reset complete.")
        return True

def convert_column_name_to_field_name(column_name):
    """Convert Excel column names to valid Python field names"""
    # Create a mapping for the specific columns we want to import
    special_mappings = {
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
    
    # Return the mapped field name if it exists
    if column_name in special_mappings:
        return special_mappings[column_name]
    
    # If the column is not in our mapping, return None to skip it
    return None

def populate_from_excel(excel_file, clear_db=False):
    """Populate the database with only the specified fields from the Excel file"""
    print(f"Reading data from {excel_file}...")
    
    # Reset the database to ensure schema is up to date
    if clear_db:
        print("Resetting database (dropping and recreating tables)...")
        if not reset_database():
            print("Failed to reset database. Aborting import.")
            return
    
    # Read the Excel file
    df = pd.read_excel(excel_file)
    
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
        print(f"Before filtering by Produkttype: {len(df_filtered)} records")
        df_filtered = df_filtered[df_filtered['Produkttype'].isin(['MI', 'FG'])]
        print(f"After filtering by Produkttype: {len(df_filtered)} records")
    
    # Create a mapping from Excel column names to database field names
    field_mapping = {}
    for column in filtered_columns:
        field_name = convert_column_name_to_field_name(column)
        if field_name:  # Only add if the field name is valid
            field_mapping[column] = field_name
    
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
    
    # Count of records processed and added
    processed = 0
    added = 0
    skipped = 0
    
    with app.app_context():
        for record in records:
            processed += 1
            
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
            
            # Only add the donor if Produkttype is MI or FG
            produkttype = donor_data.get('produkttype')
            if produkttype in ['MI', 'FG']:
                try:
                    new_donor = RecurringDonor(**donor_data)
                    db.session.add(new_donor)
                    added += 1
                    
                    # Commit every 100 records to avoid large transactions
                    if added % 100 == 0:
                        db.session.commit()
                        print(f"Committed {added} records so far...")
                except Exception as e:
                    print(f"Error adding donor (record {processed}): {e}")
                    print(f"Problematic data: {donor_data}")
                    db.session.rollback()
                    skipped += 1
            else:
                skipped += 1
                if produkttype:
                    print(f"Skipped record {processed} with Produkttype: {produkttype}")
                else:
                    print(f"Skipped record {processed} with missing Produkttype")
        
        # Final commit for any remaining records
        try:
            db.session.commit()
            print(f"Successfully added {added} donors to the database.")
            print(f"Skipped {skipped} records.")
        except Exception as e:
            print(f"Error during final commit: {e}")
            db.session.rollback()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Import donor data from Excel file')
    parser.add_argument('excel_file', help='Path to the Excel file to import')
    parser.add_argument('--clear', action='store_true', help='Clear the database before importing')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.excel_file):
        print(f"Error: File {args.excel_file} does not exist.")
        sys.exit(1)
    
    populate_from_excel(args.excel_file, args.clear)
