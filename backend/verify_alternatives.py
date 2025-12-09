
from news_fetcher import get_aggregated_news, get_company_info
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

tickers = ["GC=F", "BTC-USD", "^TNX", "CL=F"]

for ticker in tickers:
    print(f"\nTesting {ticker}...")
    try:
        name = get_company_info(ticker)
        print(f"Name: {name}")
        
        news = get_aggregated_news(ticker)
        print(f"Found {len(news)} articles")
        if news:
            print(f"Sample: {news[0]['title']}")
    except Exception as e:
        print(f"Error with {ticker}: {e}")
