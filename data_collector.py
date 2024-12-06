from pymongo import MongoClient
import yfinance as yf
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import certifi
import logging
from time import sleep

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB setup
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MongoDB URI not found in environment variables")

try:
    client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
    # Test the connection
    client.admin.command('ping')
    db = client.stockstream
    prices_collection = db.stock_crypto_prices
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {str(e)}")
    raise

# List of assets to track (top 5 only)
STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']  # Top 5 tech stocks
CRYPTO = ['BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'XRP-USD']  # Top 5 cryptocurrencies

def fetch_and_store_prices():
    """Fetch current prices and store in MongoDB"""
    timestamp = datetime.utcnow()
    logger.info(f"Fetching prices at {timestamp}")
    
    # Fetch and store stock prices
    for symbol in STOCKS:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price = float(info.last_price if hasattr(info, 'last_price') else 0)
            volume = float(info.volume if hasattr(info, 'volume') else 0)
            
            price_data = {
                'symbol': symbol,
                'price': price,
                'volume': volume,
                'timestamp': timestamp,
                'type': 'stock'
            }
            
            prices_collection.insert_one(price_data)
            logger.info(f"Stored stock price for {symbol}: ${price:.2f}")
            
        except Exception as e:
            logger.error(f"Error fetching stock {symbol}: {str(e)}")
    
    # Fetch and store crypto prices
    for symbol in CRYPTO:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price = float(info.last_price if hasattr(info, 'last_price') else 0)
            volume = float(info.volume if hasattr(info, 'volume') else 0)
            
            price_data = {
                'symbol': symbol,
                'price': price,
                'volume': volume,
                'timestamp': timestamp,
                'type': 'crypto'
            }
            
            prices_collection.insert_one(price_data)
            logger.info(f"Stored crypto price for {symbol}: ${price:.2f}")
            
        except Exception as e:
            logger.error(f"Error fetching crypto {symbol}: {str(e)}")

def clear_old_data():
    """Clear data older than 24 hours"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        result = prices_collection.delete_many({'timestamp': {'$lt': cutoff_time}})
        logger.info(f"Cleared {result.deleted_count} old price records")
    except Exception as e:
        logger.error(f"Error clearing old data: {str(e)}")

def run_collector():
    """Main function to run the data collection process"""
    try:
        while True:
            fetch_and_store_prices()
            sleep(3600)  # Wait for 1 hour
            clear_old_data()  # Clear old data after each collection
    except KeyboardInterrupt:
        logger.info("Data collection stopped by user")
    except Exception as e:
        logger.error(f"Error in data collection: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting price data collection...")
    run_collector()
