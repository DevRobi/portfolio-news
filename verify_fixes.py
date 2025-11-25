import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from news_fetcher import get_aggregated_news, normalize_date

def verify_fixes():
    print("--- Testing Date Normalization ---")
    dates = [
        1700000000, # Timestamp
        "1 hour ago",
        "Nov 23, 2025",
        "2025-11-23T10:00:00"
    ]
    for d in dates:
        print(f"Input: {d} -> Output: {normalize_date(d)}")

    print("\n--- Testing News Fetching & Filtering for BUR ---")
    ticker = "BUR"
    news = get_aggregated_news(ticker)
    
    print(f"Found {len(news)} articles.")
    
    burnley_count = 0
    valid_date_count = 0
    
    for article in news:
        title = article['title']
        date = article['published']
        
        print(f"[{article['source']}] {title} ({date})")
        
        if "Burnley" in title:
            burnley_count += 1
            print("  -> WARNING: Found Burnley news!")
            
        if date and "Invalid" not in date: # Simple check, ideally check ISO format
             valid_date_count += 1
             
    print(f"\nSummary:")
    print(f"Total Articles: {len(news)}")
    print(f"Burnley Articles: {burnley_count}")
    print(f"Valid Dates: {valid_date_count}/{len(news)}")
    
    if burnley_count == 0 and len(news) > 0:
        print("SUCCESS: No Burnley news found.")
    else:
        print("WARNING: Burnley news found or no news found.")

if __name__ == "__main__":
    verify_fixes()
