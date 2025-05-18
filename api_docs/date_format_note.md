# Note on Date Format Handling

## startdate Field Format

The `startdate` field in the recurring donor API has been updated to handle dates properly:

1. **API Interface**: 
   - The API accepts the date as a string in either DD.MM.YYYY format (e.g., "01.09.2023") or YYYY-MM-DD format (e.g., "2023-09-01")
   - When retrieving data, the date is returned in DD.MM.YYYY format

2. **Database Storage**:
   - The date is stored as a proper DATE type in the database
   - This allows for proper date sorting, filtering, and calculations

3. **Error Handling**:
   - If an invalid date format is provided, the API will return an error message
   - The error will specify that the date should be in DD.MM.YYYY or YYYY-MM-DD format

This approach gives you the best of both worlds - a proper date type in the database while maintaining a consistent string format in the API interface.
