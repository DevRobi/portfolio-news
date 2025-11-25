from googlesearch import search
from duckduckgo_search import DDGS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google():
    logger.info("Testing Google Search...")
    try:
        results = list(search("test", num_results=5, advanced=True))
        logger.info(f"Google Results: {len(results)}")
        for r in results:
            logger.info(f" - {r.title}")
    except Exception as e:
        logger.error(f"Google Search failed: {e}")

def test_ddg():
    logger.info("Testing DuckDuckGo...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text("test", max_results=5))
            logger.info(f"DDG Results: {len(results)}")
            for r in results:
                logger.info(f" - {r['title']}")
    except Exception as e:
        logger.error(f"DDG failed: {e}")

if __name__ == "__main__":
    test_google()
    test_ddg()
    
    from GoogleNews import GoogleNews
    logger.info("Testing GoogleNews...")
    try:
        gn = GoogleNews()
        gn.search("Burford Capital Investor Relations")
        results = gn.result()
        logger.info(f"GoogleNews Results: {len(results)}")
        for r in results:
            logger.info(f" - {r['title']}")
    except Exception as e:
        logger.error(f"GoogleNews failed: {e}")
