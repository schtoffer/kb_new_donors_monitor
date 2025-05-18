# KB FG Monitor API Documentation

This folder contains documentation and test scripts for the KB FG Monitor API endpoints.

## Available Endpoints

1. **GET /api/today** - Get today's donor statistics
2. **POST /api/donor-stats** - Update donor statistics for a specific date
3. **POST /api/new-recurring-donor** - Add or update a recurring donor
4. **GET /api/recurring-donors** - Get all recurring donors (with optional filtering)

## Authentication

All API endpoints require authentication using a Bearer token in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

The default API key for testing is `test_api_key_123`. In production, this should be set using the `VENDOR_API_KEY` environment variable.

## API Endpoints Documentation

### GET /api/today

Returns donor statistics for the current day.

**Response Example:**
```json
{
  "n_new_donors": 25,
  "yearly_sum_new_donors": 18000,
  "average_n_new_donors_last_30_days": 22
}
```

### POST /api/donor-stats

Updates donor statistics for a specific date.

**Request Body:**
```json
{
  "date": "2025-05-18",
  "n_new_donors": 25,
  "yearly_sum_new_donors": 18000,
  "n_total_new_donors": 48000,
  "yearly_sum_all_donors": 67680000
}
```

**Response Example:**
```json
{
  "status": "success",
  "message": "Donor statistics updated successfully"
}
```

### POST /api/new-recurring-donor

Adds a new recurring donor or updates an existing one if the combination of `name_id` and `agreement_number` already exists.

**Request Body:**
```json
{
  "campaign_id": 132,
  "payment_method": "vippsrecurring",
  "classification_id_success": "BG",
  "name": {
    "name_id": 123,
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

**Response Example (New Donor):**
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

**Response Example (Updated Donor):**
```json
{
  "status": "success",
  "message": "Recurring donor updated successfully",
  "donor": {
    // Same structure as above
  }
}
```

### GET /api/recurring-donors

Returns all recurring donors or filters by name_id if provided as a query parameter.

**Query Parameters:**
- `name_id` (optional): Filter donors by name_id

**Example Request:**
```
GET /api/recurring-donors?name_id=Ola
```

**Response Example:**
```json
{
  "status": "success",
  "count": 2,
  "donors": [
    {
      // Donor 1 details (same structure as above)
    },
    {
      // Donor 2 details (same structure as above)
    }
  ]
}
```

## Testing

Use the provided test scripts in this folder to test the API endpoints.
