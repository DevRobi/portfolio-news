import yfinance as yf
import json
from datetime import datetime

def debug_yahoo_news(ticker):
    print(f"Fetching news for {ticker}...")
    stock = yf.Ticker(ticker)
    news = stock.news
    
    print(f"Found {len(news)} articles.")
    
    if news:
        print("\nFirst article keys:", news[0].keys())
        if 'content' in news[0]:
            print("\n'content' dictionary found. Keys:", news[0]['content'].keys())
            print(json.dumps(news[0]['content'], indent=2, default=str))
        else:
            print("\nNo 'content' dictionary found. Dumping whole item:")
            print(json.dumps(news[0], indent=2, default=str))
            
        print("\nChecking all articles for 'title' and 'providerPublishTime':")
        for i, item in enumerate(news):
            title = item.get('title', 'NO TITLE FOUND')
            pub_time = item.get('providerPublishTime', 'NO DATE FOUND')
            print(f"{i+1}. Title: {title}")
            print(f"   Date: {pub_time}")
            print("-" * 30)

if __name__ == "__main__":
    debug_yahoo_news("BUR")
