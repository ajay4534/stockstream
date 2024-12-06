import schedule
import time
from data_collector import fetch_and_store_prices, clear_old_data
from graph_generator import update_all_graphs
import logging
from datetime import datetime

# Setup logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_hourly_tasks():
    """Run tasks that need to be executed every hour"""
    try:
        logger.info("Starting hourly tasks...")
        logger.info("Fetching and storing prices...")
        fetch_and_store_prices()
        logger.info("Updating graphs...")
        update_all_graphs()
        logger.info("Hourly tasks completed successfully")
    except Exception as e:
        logger.error(f"Error in hourly tasks: {str(e)}")

def run_daily_tasks():
    """Run tasks that need to be executed daily at midnight"""
    try:
        logger.info("Starting daily cleanup...")
        clear_old_data()
        logger.info("Daily tasks completed successfully")
    except Exception as e:
        logger.error(f"Error in daily tasks: {str(e)}")

def main():
    logger.info("Starting StockStream scheduler...")
    
    # Run tasks immediately on startup
    logger.info("Running initial tasks...")
    run_hourly_tasks()
    
    # Schedule hourly tasks
    schedule.every().hour.at(":00").do(run_hourly_tasks)
    logger.info("Scheduled hourly tasks")
    
    # Schedule daily tasks at midnight
    schedule.every().day.at("00:00").do(run_daily_tasks)
    logger.info("Scheduled daily tasks")
    
    logger.info("Scheduler started successfully")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Error in scheduler: {str(e)}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main()
