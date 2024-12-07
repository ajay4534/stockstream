from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os
import requests
import json
from pymongo import MongoClient
import logging
import certifi
from datetime import datetime, timedelta
import yfinance as yf

# Load environment variables
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB setup
MONGODB_URI = os.getenv('MONGODB_URI')
try:
    client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
    db = client.stockstream
    lottery_collection = db.lottery_results
    prices_collection = db.prices
    logger.info("Successfully connected to MongoDB Atlas")
except Exception as e:
    logger.error(f"Error connecting to MongoDB Atlas: {str(e)}")
    db = None

# Market data endpoints
STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']  # Top 5 stocks
CRYPTO = ['BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'XRP-USD']  # Top 5 cryptos

@app.route('/api/market/summary')
def get_market_summary():
    try:
        # Fetch data for major indices and BTC
        symbols = ['^GSPC', '^IXIC', 'BTC-USD']
        data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.fast_info  # Use fast_info instead of info
                current = float(info.last_price if hasattr(info, 'last_price') else 0)
                prev_close = float(info.previous_close if hasattr(info, 'previous_close') else current)
                change = ((current - prev_close) / prev_close * 100) if prev_close else 0
                
                data[symbol] = {
                    'price': current,
                    'change': round(change, 2)
                }
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
                data[symbol] = {
                    'price': 0,
                    'change': 0
                }
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return jsonify({'error': 'Failed to fetch market data'}), 500

@app.route('/api/market/movers')
def get_market_movers():
    try:
        # List of popular stocks to track
        symbols = STOCKS
        movers = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.fast_info  # Use fast_info instead of info
                current = float(info.last_price if hasattr(info, 'last_price') else 0)
                prev_close = float(info.previous_close if hasattr(info, 'previous_close') else current)
                change = ((current - prev_close) / prev_close * 100) if prev_close else 0
                
                movers.append({
                    'symbol': symbol,
                    'price': current,
                    'change': round(change, 2)
                })
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
                continue
        
        # Sort by absolute change percentage
        movers.sort(key=lambda x: abs(x['change']), reverse=True)
        return jsonify(movers[:5])  # Return top 5 movers
    except Exception as e:
        logger.error(f"Error fetching market movers: {str(e)}")
        return jsonify({'error': 'Failed to fetch market movers'}), 500

@app.route('/api/historical/<symbol>')
def get_historical_data(symbol):
    try:
        timeframe = request.args.get('timeframe', '1d')
        
        # Convert timeframe to yfinance interval and period
        intervals = {
            '1d': ('5m', '1d'),
            '1w': ('15m', '1wk'),
            '1m': ('1d', '1mo'),
            '1y': ('1d', '1y')
        }
        
        interval, period = intervals.get(timeframe, ('5m', '1d'))
        
        # Fetch historical data
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period, interval=interval)
        
        # Convert timestamps to string format and ensure all values are JSON serializable
        data = {
            'timestamps': [ts.strftime('%Y-%m-%d %H:%M:%S') for ts in history.index],
            'prices': [float(price) for price in history['Close'].tolist()]
        }
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching historical data: {str(e)}")
        return jsonify({'error': 'Failed to fetch historical data'}), 500

@app.route('/api/stocks/search')
def stocks_search():
    try:
        query = request.args.get('q', '').upper()
        if not query:
            return jsonify([])
        
        # List of major stocks for demo
        demo_stocks = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'META': 'Meta Platforms Inc.',
            'NVDA': 'NVIDIA Corporation'
        }
        
        # Filter stocks based on query
        matching_symbols = [
            {'symbol': symbol, 'name': name}
            for symbol, name in demo_stocks.items()
            if query in symbol or query.lower() in name.lower()
        ]
        
        return jsonify(matching_symbols)
    except Exception as e:
        logger.error(f"Error searching stocks: {str(e)}")
        return jsonify({'error': 'Failed to search stocks'}), 500

@app.route('/api/crypto/search')
def crypto_search():
    try:
        query = request.args.get('q', '').upper()
        if not query:
            return jsonify([])
        
        # Demo list of cryptocurrencies
        demo_crypto = {
            'BTC-USD': 'Bitcoin',
            'ETH-USD': 'Ethereum',
            'DOGE-USD': 'Dogecoin',
            'ADA-USD': 'Cardano',
            'SOL-USD': 'Solana'
        }
        
        # Filter crypto based on query
        matching_symbols = [
            {'symbol': symbol, 'name': name}
            for symbol, name in demo_crypto.items()
            if query in symbol or query.lower() in name.lower()
        ]
        
        return jsonify(matching_symbols)
    except Exception as e:
        logger.error(f"Error searching cryptocurrencies: {str(e)}")
        return jsonify({'error': 'Failed to search cryptocurrencies'}), 500

@app.route('/api/lottery/latest')
def get_lottery_results():
    try:
        current_date = datetime(2024, 12, 7, 13, 56, 23)  # Using the provided time
        mock_data = {
            'powerball': {
                'old_draw_date': '2024-12-04',  # Previous Wednesday
                'old_numbers': '02 11 22 35 60',
                'old_powerball': '23',
                'latest_draw_date': '2024-12-06',  # Latest Friday
                'latest_numbers': '12 24 36 48 60',
                'latest_powerball': '15',
                'next_draw_date': '2024-12-09',  # Next Monday
                'estimated_jackpot': '$815 Million'
            },
            'mega_millions': {
                'old_draw_date': '2024-12-03',  # Previous Tuesday
                'old_numbers': '15 28 37 49 65',
                'old_mega_ball': '12',
                'latest_draw_date': '2024-12-06',  # Latest Friday
                'latest_numbers': '07 15 29 38 42',
                'latest_mega_ball': '18',
                'next_draw_date': '2024-12-10',  # Next Tuesday
                'estimated_jackpot': '$415 Million'
            }
        }
        return jsonify(mock_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Price data routes
@app.route('/api/current_prices')
def get_current_prices():
    try:
        asset_type = request.args.get('type', 'stock')
        symbols = STOCKS if asset_type == 'stock' else CRYPTO
        
        # Define common names for assets
        asset_names = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corp.',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'NVDA': 'NVIDIA Corp.',
            'BTC-USD': 'Bitcoin',
            'ETH-USD': 'Ethereum',
            'BNB-USD': 'Binance Coin',
            'SOL-USD': 'Solana',
            'XRP-USD': 'Ripple'
        }
        
        assets = []
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.fast_info
                current = float(info.last_price if hasattr(info, 'last_price') else 0)
                prev_close = float(info.previous_close if hasattr(info, 'previous_close') else current)
                change = ((current - prev_close) / prev_close * 100) if prev_close else 0
                
                if current == 0:
                    logger.error(f"Got zero price for {symbol}, skipping")
                    continue
                    
                assets.append({
                    'symbol': symbol,
                    'name': asset_names.get(symbol, symbol),
                    'price': current,
                    'change': round(change, 2)
                })
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
                continue
        
        if not assets:
            return jsonify({'error': 'No asset data available'}), 500
            
        return jsonify(assets)
    except Exception as e:
        logger.error(f"Error fetching current prices: {str(e)}")
        return jsonify({'error': 'Failed to fetch current prices'}), 500

@app.route('/api/dashboard/graphs')
def get_dashboard_graphs():
    try:
        # Get historical data for stocks
        stock_data = []
        for symbol in STOCKS[:5]:  # Only top 5 stocks
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period='1d', interval='5m')
                if not history.empty:
                    stock_data.append({
                        'x': [ts.strftime('%H:%M') for ts in history.index],
                        'y': [float(price) for price in history['Close'].tolist()],
                        'name': symbol,
                        'type': 'scatter',
                        'mode': 'lines+markers'
                    })
            except Exception as e:
                logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
                continue
        
        # Get historical data for crypto
        crypto_data = []
        for symbol in CRYPTO[:5]:  # Only top 5 cryptos
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period='1d', interval='5m')
                if not history.empty:
                    crypto_data.append({
                        'x': [ts.strftime('%H:%M') for ts in history.index],
                        'y': [float(price) for price in history['Close'].tolist()],
                        'name': symbol,
                        'type': 'scatter',
                        'mode': 'lines+markers'
                    })
            except Exception as e:
                logger.error(f"Error fetching crypto data for {symbol}: {str(e)}")
                continue
        
        # Check if we have any data
        if not stock_data and not crypto_data:
            return jsonify({'error': 'No historical data available'}), 500

        # Create graph configurations
        stocks_layout = {
            'title': 'Stock Performance (24h)',
            'xaxis': {'title': 'Time'},
            'yaxis': {'title': 'Price ($)'},
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2},
            'margin': {'l': 60, 'r': 30, 't': 40, 'b': 80},
            'height': 500,  # Make it taller
            'plot_bgcolor': '#ffffff',
            'paper_bgcolor': '#ffffff',
            'hovermode': 'x unified'  # Show all values at the same x position
        }

        crypto_layout = {
            'title': 'Cryptocurrency Performance (24h)',
            'xaxis': {'title': 'Time'},
            'yaxis': {'title': 'Price ($)'},
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': -0.2},
            'margin': {'l': 60, 'r': 30, 't': 40, 'b': 80},
            'height': 500,  # Make it taller
            'plot_bgcolor': '#ffffff',
            'paper_bgcolor': '#ffffff',
            'hovermode': 'x unified'  # Show all values at the same x position
        }

        return jsonify({
            'stocks': {
                'data': stock_data,
                'layout': stocks_layout
            },
            'crypto': {
                'data': crypto_data,
                'layout': crypto_layout
            }
        })
    except Exception as e:
        logger.error(f"Error generating dashboard graphs: {str(e)}")
        return jsonify({'error': 'Failed to generate graphs'}), 500

@app.route('/api/dashboard/summary')
def get_dashboard_summary():
    try:
        # Get market summary data
        indices = {'^GSPC': 'S&P 500', '^IXIC': 'NASDAQ'}
        market_data = {}
        
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.fast_info
                current = float(info.last_price if hasattr(info, 'last_price') else 0)
                prev_close = float(info.previous_close if hasattr(info, 'previous_close') else current)
                change = ((current - prev_close) / prev_close * 100) if prev_close else 0
                
                market_data[name] = {
                    'price': current,
                    'change': round(change, 2)
                }
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
        
        # Get top stocks and crypto from MongoDB
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Get latest stock data
        stocks = list(prices_collection.find({
            'type': 'stock',
            'timestamp': {'$gte': cutoff_time}
        }).sort('timestamp', -1).limit(5))
        
        # Get latest crypto data
        crypto = list(prices_collection.find({
            'type': 'crypto',
            'timestamp': {'$gte': cutoff_time}
        }).sort('timestamp', -1).limit(5))
        
        return jsonify({
            'market_indices': market_data,
            'top_stocks': stocks,
            'top_crypto': crypto
        })
        
    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {str(e)}")
        return jsonify({'error': 'Failed to fetch dashboard data'}), 500

# Add routes for dedicated views
@app.route('/stocks')
def stocks_view():
    # Get user's saved stocks
    saved_stocks = STOCKS  # Default list for now
    
    # Fetch current data for saved stocks
    stocks_data = []
    for symbol in saved_stocks:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            current = float(info.last_price if hasattr(info, 'last_price') else 0)
            prev_close = float(info.previous_close if hasattr(info, 'previous_close') else current)
            change = ((current - prev_close) / prev_close * 100) if prev_close else 0
            
            stocks_data.append({
                'symbol': symbol,
                'price': current,
                'change': round(change, 2)
            })
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            continue
    
    return jsonify(stocks_data)

@app.route('/crypto')
def crypto_view():
    # Get user's saved cryptocurrencies
    saved_crypto = CRYPTO  # Default list for now
    
    # Fetch current data for saved cryptocurrencies
    crypto_data = []
    for symbol in saved_crypto:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            current = float(info.last_price if hasattr(info, 'last_price') else 0)
            prev_close = float(info.previous_close if hasattr(info, 'previous_close') else current)
            change = ((current - prev_close) / prev_close * 100) if prev_close else 0
            
            crypto_data.append({
                'symbol': symbol,
                'price': current,
                'change': round(change, 2)
            })
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            continue
    
    return jsonify(crypto_data)

@app.route('/lottery/saved')
def lottery_saved():
    try:
        # Get saved lottery numbers from MongoDB
        saved_numbers = {
            'powerball': {
                'numbers': ['05', '12', '23', '34', '45'],  # Default numbers for now
                'powerball': '06'
            },
            'mega_millions': {
                'numbers': ['08', '15', '27', '36', '49'],  # Default numbers for now
                'mega_ball': '12'
            }
        }
        
        return jsonify(saved_numbers)
    except Exception as e:
        logger.error(f"Error fetching saved lottery numbers: {str(e)}")
        return jsonify({'error': 'Failed to fetch saved lottery numbers'}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
