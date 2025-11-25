import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from news_fetcher import get_aggregated_news

def test_ticker(ticker):
    print(f"\nTesting ticker: {ticker}")
    try:
        news = get_aggregated_news(ticker)
        print(f"Found {len(news)} articles.")
        for i, article in enumerate(news[:3]):
            print(f"{i+1}. {article['title']} ({article['source']})")
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")

if __name__ == "__main__":
    test_ticker("TOU")
    test_ticker("TOU.TO")
