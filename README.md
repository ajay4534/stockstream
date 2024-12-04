# StockStream

A real-time stock and cryptocurrency price tracker built with Flask and JavaScript.

## Features

- Real-time price updates every 30 seconds
- Search and track both stocks and cryptocurrencies
- Clean, modern UI with responsive design
- Easy to add and remove tracked assets
- Price history with last update time

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Dependencies

- Flask: Web framework
- requests: HTTP client for API calls
- yfinance: Yahoo Finance API wrapper

## APIs Used

- CoinGecko API for cryptocurrency data
- Yahoo Finance API for stock data

## Project Structure

```
stockstream/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
├── static/
│   ├── css/
│   │   └── style.css  # Stylesheet
│   └── js/
│       └── main.js    # Frontend JavaScript
└── templates/
    └── index.html     # Main HTML template
```
