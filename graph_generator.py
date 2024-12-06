import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
import certifi
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB setup
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
db = client.stockstream
prices_collection = db.stock_crypto_prices

def generate_performance_graph(asset_type, save_path):
    """Generate performance graph for top 5 assets of given type"""
    try:
        # Get data for the last 24 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        data = list(prices_collection.find({
            'type': asset_type,
            'timestamp': {'$gte': cutoff_time}
        }).sort('timestamp', 1))

        if not data:
            logger.warning(f"No data found for {asset_type}")
            return

        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Pivot the data for plotting
        pivot_df = df.pivot(index='timestamp', columns='symbol', values='price')
        
        # Calculate percentage change
        pct_change = ((pivot_df - pivot_df.iloc[0]) / pivot_df.iloc[0]) * 100
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        for column in pct_change.columns:
            plt.plot(pct_change.index, pct_change[column], label=column, linewidth=2)
        
        plt.title(f'Top 5 {asset_type.capitalize()}s Performance (24h)')
        plt.xlabel('Time (UTC)')
        plt.ylabel('Percentage Change (%)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(save_path)
        plt.close()
        
        logger.info(f"Generated {asset_type} performance graph")
    except Exception as e:
        logger.error(f"Error generating {asset_type} graph: {str(e)}")

def update_all_graphs():
    """Update all performance graphs"""
    try:
        # Ensure static/graphs directory exists
        graphs_dir = os.path.join(os.path.dirname(__file__), 'static', 'graphs')
        os.makedirs(graphs_dir, exist_ok=True)
        
        # Generate graphs for stocks and crypto
        generate_performance_graph('stock', os.path.join(graphs_dir, 'stocks_performance.png'))
        generate_performance_graph('crypto', os.path.join(graphs_dir, 'crypto_performance.png'))
        
        logger.info("All graphs updated successfully")
    except Exception as e:
        logger.error(f"Error updating graphs: {str(e)}")

if __name__ == "__main__":
    update_all_graphs()
