from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId
import os
import logging
from dotenv import load_dotenv
import requests
from yahoo_fin import stock_info
import certifi

# Load environment variables
load_dotenv()

# Create Flask app with explicit template and static folders
app = Flask(
    __name__,
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates')),
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
)

app.secret_key = os.getenv('SECRET_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = app.logger

# MongoDB Atlas setup with error handling
try:
    # Use certifi for SSL certificate verification
    client = MongoClient(os.getenv('MONGO_URI'), tlsCAFile=certifi.where())
    # Test the connection
    client.admin.command('ping')
    db = client[os.getenv('MONGO_DB_NAME')]
    users_collection = db['users']
    watchlist_collection = db['watchlists']
    logger.info("Successfully connected to MongoDB Atlas")
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    logger.error(f"Failed to connect to MongoDB Atlas: {str(e)}")
    raise

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data
        self.id = str(user_data['_id'])  # Ensure id is string for Flask-Login

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = users_collection.find_one({'_id': ObjectId(user_id)})
        return User(user_data) if user_data else None
    except Exception as e:
        logger.error(f"Error loading user: {str(e)}")
        return None

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = users_collection.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            login_user(User(user))
            return redirect(url_for('index'))
        
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')
        
        if users_collection.find_one({'email': email}):
            flash('Email already registered')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        user_data = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'watchlist': []
        }
        
        users_collection.insert_one(user_data)
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/')
@login_required
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
@login_required
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
@login_required
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
@login_required
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
