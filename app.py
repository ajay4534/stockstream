from flask import Flask, jsonify, render_template, request
import requests
from yahoo_fin import stock_info
import os
import logging

# Create Flask app with explicit template and static folders
app = Flask(
    __name__,
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates')),
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = app.logger

# Default symbols to track
DEFAULT_CRYPTO = ['bitcoin', 'ethereum', 'dogecoin']
DEFAULT_STOCKS = ['MSFT', 'SPY', 'DIA', 'TSLA']

def get_crypto_prices(symbols):
    """
    Fetch cryptocurrency prices using CoinGecko API.
    """
    try:
        if not symbols:
            return {}
        
        symbols_str = ','.join(symbols)
        response = requests.get(
            f'https://api.coingecko.com/api/v3/simple/price?ids={symbols_str}&vs_currencies=usd'
        )
        response.raise_for_status()
        data = response.json()
        return {symbol: {'price': price['usd'], 'type': 'crypto'} for symbol, price in data.items()}
    except Exception as e:
        logger.error(f"Error fetching crypto prices: {e}")
        return {}

def get_stock_prices(symbols):
    """
    Fetch stock prices using Yahoo Finance.
    """
    data = {}
    for symbol in symbols:
        try:
            current_price = stock_info.get_live_price(symbol)
            if current_price:
                logger.info(f"Got price for {symbol}: ${current_price}")
                data[symbol] = {'price': float(current_price), 'type': 'stock'}
            else:
                logger.warning(f"No price data available for {symbol}")
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            continue
    
    logger.info(f"Final stock data: {data}")
    return data

@app.route('/')
def index():
    """
    Render the main page with default tracked assets.
    """
    return render_template(
        'index.html',
        default_crypto=DEFAULT_CRYPTO,
        default_stocks=DEFAULT_STOCKS
    )

@app.route('/get_prices')
def get_prices():
    """
    Endpoint to fetch prices for both cryptocurrencies and stocks.
    """
    crypto_symbols = request.args.get('crypto', '').strip()
    stock_symbols = request.args.get('stocks', '').strip()
    
    prices = {}

    # Fetch cryptocurrency prices
    if crypto_symbols:
        try:
            crypto_list = crypto_symbols.split(',')
            prices.update(get_crypto_prices(crypto_list))
        except Exception as e:
            logger.error(f"Error processing crypto symbols: {e}")
    
    # Fetch stock prices
    if stock_symbols:
        try:
            stock_list = stock_symbols.split(',')
            prices.update(get_stock_prices(stock_list))
        except Exception as e:
            logger.error(f"Error processing stock symbols: {e}")
    
    return jsonify(prices)

@app.route('/search_coins')
def search_coins():
    """
    Search for cryptocurrencies using CoinGecko API.
    """
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    try:
        response = requests.get(f'https://api.coingecko.com/api/v3/search?query={query}')
        response.raise_for_status()
        data = response.json()
        coins = data.get('coins', [])
        return jsonify([{'id': coin['id'], 'name': coin['name']} for coin in coins[:5]])
    except Exception as e:
        logger.error(f"Error searching coins: {e}")
        return jsonify([])

@app.route('/search_stocks')
def search_stocks():
    """
    Search for stocks using Yahoo Finance.
    """
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    try:
        # For simplicity, just return the queried symbol as a stock
        # You can enhance this with a proper stock search API if needed
        return jsonify([{
            'symbol': query.upper(),
            'name': query.upper()
        }])
    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
