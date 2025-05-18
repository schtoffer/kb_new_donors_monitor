# KB FG Monitor API Documentation

## Overview

This document provides detailed information about the KB FG Monitor API endpoints, including request formats, response examples, and authentication requirements.

## Authentication

All API endpoints require authentication using a Bearer token in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

The default API key for testing is `test_api_key_123`. In production, this should be set using the `VENDOR_API_KEY` environment variable.

## API Endpoints

### 1. Donor Statistics

#### GET /api/today

Returns donor statistics for the current day.

**Request:**
```
GET /api/today
Authorization: Bearer YOUR_API_KEY
```

**Response:**
```json
{
  "n_new_donors": 25,
  "yearly_sum_new_donors": 18000,
  "average_n_new_donors_last_30_days": 22
}
```

**Status Codes:**
- 200: Success
- 404: No data for today
- 401: Unauthorized

#### POST /api/donor-stats

Updates donor statistics for a specific date.

**Request:**
```
POST /api/donor-stats
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "date": "2025-05-18",
  "n_new_donors": 25,
  "yearly_sum_new_donors": 18000,
  "n_total_new_donors": 48000,
  "yearly_sum_all_donors": 67680000
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Donor statistics updated successfully"
}
```

**Status Codes:**
- 200: Success
- 400: Bad request (missing or invalid fields)
- 401: Unauthorized
- 500: Server error

### 2. Recurring Donors

#### POST /api/new-recurring-donor

Adds a new recurring donor or updates an existing one if the combination of `name_id` and `agreement_number` already exists.

**Request:**
```
POST /api/new-recurring-donor
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "campaign_id": 132,
  "payment_method": "vippsrecurring",
  "classification_id_success": "BG",
  "name": {
    "name_id": "Ola",
    "zip": "4601",
    "country_id": "NO",
    "nametype_id": "D"
  },
  "agreement": {
    "agreement_number": "123456",
    "producttype_id": "FG",
    "project_id": 0,
    "productvariant_id": null,
    "amount": 100,
    "interval": "Monthly",
    "startdate": "01.09.2023"
  }
}
```

**Field Descriptions:**

Top-level fields:
- `campaign_id` (integer): The campaign identifier
- `payment_method` (string): Method of payment (e.g., "vippsrecurring")
- `classification_id_success` (string): Classification identifier

Name fields:
- `name_id` (integer): Unique identifier for the donor
- `zip` (string): Postal code
- `country_id` (string): Country code
- `nametype_id` (string): Type of name identifier

Agreement fields:
- `agreement_number` (string): Unique agreement identifier
- `producttype_id` (string): Product type identifier
- `project_id` (integer): Project identifier
- `productvariant_id` (integer, nullable): Product variant identifier
- `amount` (number): Donation amount
- `interval` (string): Payment interval (e.g., "Monthly")
- `startdate` (string): Start date of the agreement in DD.MM.YYYY format (e.g., "01.09.2023") or YYYY-MM-DD format (e.g., "2023-09-01"). This is stored as a proper date in the database but accepted and returned as a string in the API.

**Response (New Donor):**
```json
{
  "status": "success",
  "message": "Recurring donor created successfully",
  "donor": {
    "id": 1,
    "created_at": "2025-05-18T11:30:00.000Z",
    "updated_at": "2025-05-18T11:30:00.000Z",
    "campaign_id": 132,
    "payment_method": "vippsrecurring",
    "classification_id_success": "BG",
    "name": {
      "name_id": "Ola",
      "zip": "4601",
      "country_id": "NO",
      "nametype_id": "D"
    },
    "agreement": {
      "agreement_number": "123456",
      "producttype_id": "FG",
      "project_id": 0,
      "productvariant_id": null,
      "amount": 100,
      "interval": "Monthly",
      "startdate": "01.09.2023"
    }
  }
}
```

**Response (Updated Donor):**
```json
{
  "status": "success",
  "message": "Recurring donor updated successfully",
  "donor": {
    // Same structure as above
  }
}
```

**Status Codes:**
- 200: Success (donor updated)
- 201: Success (new donor created)
- 400: Bad request (missing or invalid fields)
- 401: Unauthorized
- 500: Server error

#### GET /api/recurring-donors

Returns all recurring donors or filters by name_id if provided as a query parameter.

**Request:**
```
GET /api/recurring-donors
Authorization: Bearer YOUR_API_KEY
```

**Query Parameters:**
- `name_id` (optional): Filter donors by name_id

**Example Filtered Request:**
```
GET /api/recurring-donors?name_id=Ola
Authorization: Bearer YOUR_API_KEY
```

**Response:**
```json
{
  "status": "success",
  "count": 2,
  "donors": [
    {
      "id": 1,
      "created_at": "2025-05-18T11:30:00.000Z",
      "updated_at": "2025-05-18T11:30:00.000Z",
      "campaign_id": 132,
      "payment_method": "vippsrecurring",
      "classification_id_success": "BG",
      "name": {
        "name_id": "Ola",
        "zip": "4601",
        "country_id": "NO",
        "nametype_id": "D"
      },
      "agreement": {
        "agreement_number": "123456",
        "producttype_id": "FG",
        "project_id": 0,
        "productvariant_id": null,
        "amount": 100,
        "interval": "Monthly",
        "startdate": "01.09.2023"
      }
    },
    {
      // Second donor details
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized
- 500: Server error

## Database Schema

### DonorStats Table
- `id` (Integer, Primary Key)
- `date` (Date, Unique)
- `n_new_donors` (Integer)
- `yearly_sum_new_donors` (Float)
- `n_total_new_donors` (Integer)
- `yearly_sum_all_donors` (Float)

### RecurringDonor Table
- `id` (Integer, Primary Key)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `campaign_id` (Integer)
- `payment_method` (String)
- `classification_id_success` (String)
- `name_id` (String)
- `zip_code` (String)
- `country_id` (String)
- `nametype_id` (String)
- `agreement_number` (String)
- `producttype_id` (String)
- `project_id` (Integer)
- `productvariant_id` (Integer, Nullable)
- `amount` (Float)
- `interval` (String)
- `startdate` (String)

**Unique Constraint:** `name_id` and `agreement_number` combination must be unique

## Testing

Use the provided test scripts in this folder to test the API endpoints:

```bash
# Make sure the Flask application is running
cd /path/to/kb_fg_monitor
python app.py

# In a separate terminal, run the test script
cd /path/to/kb_fg_monitor
./api_docs/test_recurring_donor_api.sh
```

## Error Handling

All API endpoints return appropriate HTTP status codes and error messages in JSON format:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common error scenarios:
- Missing or invalid API key
- Missing required fields
- Invalid data formats
- Server-side errors
