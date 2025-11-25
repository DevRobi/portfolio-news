import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.news_fetcher import is_valid_source, get_ir_news, get_aggregated_news

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_zacks_filtering():
    logger.info("Testing Zacks filtering...")
    
    zacks_articles = [
        {'title': 'Stock Market News - Zacks Investment Research', 'publisher': 'Zacks', 'source': 'Zacks'},
        {'title': 'Why Burford Capital (BUR) is a Strong Buy', 'publisher': 'Zacks Research', 'source': 'Yahoo Finance'},
        {'title': 'Zacks Rank #1 (Strong Buy)', 'publisher': 'Yahoo Finance', 'source': 'Zacks'},
        {'title': 'Normal News Article', 'publisher': 'Bloomberg', 'source': 'Bloomberg'}
    ]
    
    filtered = [a for a in zacks_articles if is_valid_source(a)]
    
    if len(filtered) == 1 and filtered[0]['title'] == 'Normal News Article':
        logger.info("✅ Zacks filtering passed.")
    else:
        logger.error(f"❌ Zacks filtering failed. Result: {filtered}")

def test_ir_scraping():
    logger.info("Testing IR scraping for Burford Capital...")
    
    try:
        articles = get_ir_news('BUR', 'Burford Capital')
        if articles:
            logger.info(f"✅ IR scraping passed. Found {len(articles)} articles.")
            for a in articles[:3]:
                logger.info(f"   - {a['title']} ({a['url']})")
        else:
            logger.warning("⚠️ IR scraping returned no articles. This might be due to network issues or no recent news.")
    except Exception as e:
        logger.error(f"❌ IR scraping failed with error: {e}")

if __name__ == "__main__":
    test_zacks_filtering()
    test_ir_scraping()
