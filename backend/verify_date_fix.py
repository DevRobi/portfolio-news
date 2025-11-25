import sys
import os
import logging
import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.news_fetcher import is_recent, is_valid_source

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_date_filtering():
    logger.info("Testing Date filtering...")
    
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    old_date = today - datetime.timedelta(days=40)
    ancient_date = today - datetime.timedelta(days=365*3) # 2022-ish
    
    articles = [
        {'title': 'Recent News', 'published': today.isoformat(), 'publisher': 'Bloomberg', 'source': 'Bloomberg'},
        {'title': 'Yesterday News', 'published': yesterday.isoformat(), 'publisher': 'Bloomberg', 'source': 'Bloomberg'},
        {'title': 'Old News (40 days)', 'published': old_date.isoformat(), 'publisher': 'Bloomberg', 'source': 'Bloomberg'},
        {'title': 'Ancient News (3 years)', 'published': ancient_date.isoformat(), 'publisher': 'Bloomberg', 'source': 'Bloomberg'},
        {'title': 'No Date News', 'published': None, 'publisher': 'Bloomberg', 'source': 'Bloomberg'}
    ]
    
    logger.info(f"Testing with {len(articles)} articles...")
    
    filtered = [a for a in articles if is_valid_source(a)]
    
    logger.info(f"Filtered down to {len(filtered)} articles.")
    
    titles = [a['title'] for a in filtered]
    logger.info(f"Kept titles: {titles}")
    
    if 'Recent News' in titles and 'Yesterday News' in titles and 'No Date News' in titles:
        if 'Old News (40 days)' not in titles and 'Ancient News (3 years)' not in titles:
            logger.info("✅ Date filtering passed.")
        else:
            logger.error("❌ Date filtering failed: Old articles were not filtered out.")
    else:
        logger.error("❌ Date filtering failed: Recent articles were filtered out.")

if __name__ == "__main__":
    test_date_filtering()
