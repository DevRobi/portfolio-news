import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from news_fetcher import get_aggregated_news

def test_dates():
    ticker = "BUR"
    print(f"Testing date formats for {ticker}...")
    news = get_aggregated_news(ticker)
    
    print(f"\nFound {len(news)} articles.\n")
    
    invalid_count = 0
    valid_count = 0
    
    for i, article in enumerate(news[:10], 1):  # Show first 10
        date = article.get('published')
        source = article.get('source')
        title = article.get('title')[:60] + "..." if len(article.get('title', '')) > 60 else article.get('title')
        
        if date:
            valid_count += 1
            print(f"{i}. [{source}] {title}")
            print(f"   Date: {date} ✓")
        else:
            invalid_count += 1
            print(f"{i}. [{source}] {title}")
            print(f"   Date: None ⚠️")
    
    print(f"\n{'='*60}")
    print(f"Valid Dates: {valid_count}")
    print(f"Invalid/Missing Dates: {invalid_count}")
    
    if invalid_count == 0:
        print("✅ SUCCESS: All dates normalized!")
    else:
        print(f"⚠️ WARNING: {invalid_count} articles without dates")

if __name__ == "__main__":
    test_dates()
