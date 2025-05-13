# Donor Statistics API Documentation

## Authentication

All API requests require authentication using a Bearer token in the Authorization header.

```
Authorization: Bearer your_api_key_here
```

Contact the administrator to obtain your API key.

## Endpoints

### POST /api/donor-stats

Update or create donor statistics for a specific date.

#### Request

- Method: POST
- Content-Type: application/json
- Authentication: Bearer token

#### Request Body

```json
{
  "date": "2025-05-13",
  "n_new_donors": 25,
  "yearly_sum_new_donors": 18000,
  "n_total_new_donors": 48500,
  "yearly_sum_all_donors": 68000000
}
```

| Field | Type | Description |
|-------|------|-------------|
| date | string | Date in YYYY-MM-DD format |
| n_new_donors | integer | Number of new donors for the specified date |
| yearly_sum_new_donors | number | Yearly sum from new donors (in NOK) |
| n_total_new_donors | integer | Total number of new donors year-to-date |
| yearly_sum_all_donors | number | Yearly sum from all donors (in NOK) |

#### Responses

**Success (200 OK)**

```json
{
  "status": "success",
  "message": "Donor statistics updated successfully"
}
```

**Bad Request (400)**

```json
{
  "error": "Missing required field: date"
}
```

**Unauthorized (401)**

```json
{
  "error": "Missing or invalid authorization header"
}
```

or

```json
{
  "error": "Invalid API key"
}
```

**Server Error (500)**

```json
{
  "error": "Error message details"
}
```

## Example Usage

### cURL

```bash
curl -X POST \
  https://your-domain.com/api/donor-stats \
  -H 'Authorization: Bearer test_api_key_123' \
  -H 'Content-Type: application/json' \
  -d '{
    "date": "2025-05-13",
    "n_new_donors": 25,
    "yearly_sum_new_donors": 18000,
    "n_total_new_donors": 48500,
    "yearly_sum_all_donors": 68000000
  }'
```

### Python

```python
import requests
import json

url = "https://your-domain.com/api/donor-stats"
api_key = "test_api_key_123"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "date": "2025-05-13",
    "n_new_donors": 25,
    "yearly_sum_new_donors": 18000,
    "n_total_new_donors": 48500,
    "yearly_sum_all_donors": 68000000
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())
```

## Security Considerations

- Keep your API key secure and do not share it publicly
- All requests should be made over HTTPS to ensure data security
- API keys can be rotated by contacting the administrator
