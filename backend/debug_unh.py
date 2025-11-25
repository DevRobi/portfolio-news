import sys
import os
import logging
import time
import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.news_fetcher import get_aggregated_news

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_unh_fetching():
    ticker = "UNH"
    logger.info(f"Starting debug fetch for {ticker}...")
    
    start_time = time.time()
    
    try:
        # This calls all the individual fetchers
        articles = get_aggregated_news(ticker)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"✅ Fetching completed in {duration:.2f} seconds.")
        logger.info(f"Found {len(articles)} articles.")
        
        # Breakdown by source
        sources = {}
        for a in articles:
            s = a.get('source', 'Unknown')
            sources[s] = sources.get(s, 0) + 1
            
        for s, count in sources.items():
            logger.info(f" - {s}: {count}")
            
    except Exception as e:
        logger.error(f"❌ Fetching failed: {e}")

if __name__ == "__main__":
    debug_unh_fetching()
