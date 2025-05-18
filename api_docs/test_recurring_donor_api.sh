#!/bin/bash
# Test script for the recurring donor API endpoint

# Set the base URL - change this to match your server
BASE_URL="http://localhost:5001"
API_KEY="test_api_key_123"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing KB FG Monitor Recurring Donor API${NC}"
echo "=================================================="
echo ""

# Test 1: Create a new recurring donor
echo -e "${YELLOW}Test 1: Creating a new recurring donor${NC}"
echo "Sending POST request to $BASE_URL/api/new-recurring-donor"

curl -s -X POST "$BASE_URL/api/new-recurring-donor" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
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
}'

echo ""
echo "=================================================="
echo ""

# Test 2: Update the existing recurring donor
echo -e "${YELLOW}Test 2: Updating the existing recurring donor${NC}"
echo "Sending POST request to $BASE_URL/api/new-recurring-donor with updated data"

curl -s -X POST "$BASE_URL/api/new-recurring-donor" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
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
        "amount": 200,
        "interval": "Monthly",
        "startdate": "01.09.2023"
    }
}'

echo ""
echo "=================================================="
echo ""

# Test 3: Create a new recurring donor with same name_id but different agreement_number
echo -e "${YELLOW}Test 3: Creating a new recurring donor with same name_id but different agreement_number${NC}"
echo "Sending POST request to $BASE_URL/api/new-recurring-donor"

curl -s -X POST "$BASE_URL/api/new-recurring-donor" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "campaign_id": 133,
    "payment_method": "vippsrecurring",
    "classification_id_success": "BG",
    "name": {
        "name_id": 123,
        "zip": "4601",
        "country_id": "NO",
        "nametype_id": "D"
    },
    "agreement": {
        "agreement_number": "654321",
        "producttype_id": "FG",
        "project_id": 0,
        "productvariant_id": null,
        "amount": 150,
        "interval": "Monthly",
        "startdate": "01.10.2023"
    }
}'

echo ""
echo "=================================================="
echo ""

# Test 4: Get all recurring donors
echo -e "${YELLOW}Test 4: Getting all recurring donors${NC}"
echo "Sending GET request to $BASE_URL/api/recurring-donors"

curl -s -X GET "$BASE_URL/api/recurring-donors" \
  -H "Authorization: Bearer $API_KEY"

echo ""
echo "=================================================="
echo ""

# Test 5: Getting recurring donors filtered by name_id
echo -e "${YELLOW}Test 5: Getting recurring donors filtered by name_id${NC}"
echo "Sending GET request to $BASE_URL/api/recurring-donors?name_id=123"

curl -s -X GET "$BASE_URL/api/recurring-donors?name_id=123" \
  -H "Authorization: Bearer $API_KEY"

echo ""
echo "=================================================="
echo -e "${GREEN}All tests completed!${NC}"
