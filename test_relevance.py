import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from news_fetcher import get_aggregated_news, get_company_info

def test_company_name():
    ticker = "BUR"
    company_name = get_company_info(ticker)
    print(f"Company name for {ticker}: {company_name}")
    print()

def test_news_relevance():
    ticker = "BUR"
    print(f"Testing news relevance for {ticker}...")
    news = get_aggregated_news(ticker)
    
    print(f"\nFound {len(news)} articles.")
    
    irrelevant_keywords = ["Burkina", "Bur Oak", "BURS", "Burnley"]
    irrelevant_count = 0
    
    for article in news[:20]:  # Show first 20
        title = article['title']
        source = article['source']
        
        is_irrelevant = any(keyword.lower() in title.lower() for keyword in irrelevant_keywords)
        marker = " ⚠️ IRRELEVANT" if is_irrelevant else ""
        
        print(f"[{source}] {title}{marker}")
        
        if is_irrelevant:
            irrelevant_count += 1
    
    print(f"\n{'='*60}")
    print(f"Total Articles: {len(news)}")
    print(f"Irrelevant Articles: {irrelevant_count}")
    print(f"Relevance Rate: {((len(news) - irrelevant_count) / len(news) * 100):.1f}%" if len(news) > 0 else "N/A")
    
    if irrelevant_count == 0:
        print("✅ SUCCESS: All news appears relevant!")
    else:
        print(f"⚠️ WARNING: {irrelevant_count} irrelevant articles found")

if __name__ == "__main__":
    test_company_name()
    test_news_relevance()
