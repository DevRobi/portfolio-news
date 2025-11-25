import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from news_fetcher import get_yahoo_news
import json

def verify_fix():
    print("Fetching Yahoo News for BUR...")
    articles = get_yahoo_news("BUR")
    
    print(f"\nFound {len(articles)} articles.")
    
    for i, article in enumerate(articles):
        print(f"\nArticle {i+1}:")
        print(f"Title: {article.get('title')}")
        print(f"Date: {article.get('published')}")
        print(f"URL: {article.get('url')}")
        
        if article.get('title') == 'NO TITLE FOUND' or not article.get('title'):
            print("❌ FAIL: Title missing")
        else:
            print("✅ PASS: Title present")
            
        if article.get('published') == 'NO DATE FOUND' or not article.get('published'):
            print("❌ FAIL: Date missing")
        else:
            print("✅ PASS: Date present")

if __name__ == "__main__":
    verify_fix()
