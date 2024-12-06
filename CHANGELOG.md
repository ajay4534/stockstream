# Changelog

All notable changes to the StockStream project will be documented in this file.

## [Unreleased]

## [2024.01] - 2024-01-XX

### Fixed
- Fixed 404 error in price updates by correcting the API endpoint URL in `main.js` from `/get_prices` to `/api/prices`

### Changed
- Simplified lottery page format and display
  - Removed year-based filter from lottery tab
  - Updated `lottery.html` to show only latest results
  - Streamlined lottery results display in `index.html`
  - Modified JavaScript functions in `main.js` for simplified lottery display

### Added
- Automatic refresh functionality for lottery results (5-minute intervals)
- Public access to latest lottery results through `/api/lottery/latest` endpoint

### Removed
- Year-based filtering functionality for lottery results
- Historical data section from lottery display
- Game selection functionality (now showing both games simultaneously)

### Security
- Modified `/api/lottery/latest` endpoint to be publicly accessible
- Maintained authentication requirement for main `/lottery` route

### API Integration
- Continued integration with:
  - Powerball API: `https://data.ny.gov/resource/d6yy-54nr.json`
  - Mega Millions API: `https://data.ny.gov/resource/5xaw-6ayf.json`

### Dependencies
- Flask (Web Framework)
- MongoDB (Database)
- Python Requests (API calls)
- Frontend libraries for UI functionality

### Configuration
- Environment variables maintained in `.env`:
  - `MONGO_URI`: MongoDB connection string
  - `MONGO_DB_NAME`: Database name
  - `SECRET_KEY`: Session management key

### Performance
- Implemented automatic refresh for lottery results
- Optimized API calls to reduce server load

## Notes
- Monitor automatic refresh performance
- Consider implementing error handling for API failures
- Maintain simplified design in future updates
