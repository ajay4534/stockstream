from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URI)
db = client['stockstream']
collection = db['stock_crypto_prices']

# Create indexes for better query performance
def setup_indexes():
    collection.create_index([("symbol", 1)])
    collection.create_index([("timestamp", -1)])
    collection.create_index([("type", 1)])  # type: 'stock' or 'crypto'

# Schema validation
price_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["symbol", "price", "timestamp", "type"],
        "properties": {
            "symbol": {
                "bsonType": "string",
                "description": "Stock/Crypto symbol - required"
            },
            "price": {
                "bsonType": "double",
                "description": "Current price - required"
            },
            "timestamp": {
                "bsonType": "date",
                "description": "Timestamp of the price - required"
            },
            "type": {
                "enum": ["stock", "crypto"],
                "description": "Type of asset - required"
            },
            "volume": {
                "bsonType": "double",
                "description": "Trading volume - optional"
            },
            "change_24h": {
                "bsonType": "double",
                "description": "24-hour price change - optional"
            }
        }
    }
}

def setup_database():
    try:
        db.command("collMod", "stock_crypto_prices", validator=price_schema)
    except Exception:
        db.create_collection("stock_crypto_prices", validator=price_schema)
    setup_indexes()

if __name__ == "__main__":
    setup_database()
