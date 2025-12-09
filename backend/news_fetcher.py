import yfinance as yf
from newspaper import Article
from GoogleNews import GoogleNews
import logging
import requests
import dateparser
import time
import random
import datetime
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_date(date_input):
    """Normalizes various date formats to ISO 8601 string for JavaScript compatibility."""
    if not date_input:
        return None
    
    try:
        # Handle Unix timestamps (from Yahoo Finance)
        if isinstance(date_input, (int, float)):
            return datetime.datetime.fromtimestamp(date_input).isoformat()
        
        # Parse other date formats using dateparser
        parsed_date = dateparser.parse(str(date_input))
        if parsed_date:
            return parsed_date.isoformat()
            
        return None  # Return None instead of invalid string
    except Exception as e:
        logger.debug(f"Error normalizing date '{date_input}': {e}")
        return None

def get_company_info(ticker: str):
    """Fetches company name and other info from ticker."""
    try:
        stock = yf.Ticker(ticker)
        # Use 'or ticker' to handle case where key exists but value is None
        return stock.info.get('longName') or ticker
    except:
        return ticker

def is_recent(date_str: str, days: int = 30) -> bool:
    """
    Checks if the given date string is within the last 'days' days.
    Returns True if recent or if date is None (to be safe/permissive if parsing fails),
    False if definitely older.
    """
    if not date_str:
        return True
        
    try:
        # date_str is expected to be ISO format from normalize_date
        dt = datetime.datetime.fromisoformat(date_str)
        # If timezone aware, convert to naive or handle properly. 
        # normalize_date returns ISO strings which might have offsets.
        # Let's use dateparser again to be safe or just compare timestamps if possible.
        # Actually, since we control normalize_date, we know it returns ISO.
        
        # Simplest way to handle potential timezone mismatch:
        if dt.tzinfo:
            now = datetime.datetime.now(dt.tzinfo)
        else:
            now = datetime.datetime.now()
            
        delta = now - dt
        return delta.days <= days
    except Exception as e:
        logger.debug(f"Error checking recency for {date_str}: {e}")
        return True # Default to keeping it if we can't parse, to avoid losing data

def is_valid_source(article: dict) -> bool:
    """
    Filters out unwanted sources, specifically Zacks Research.
    Returns True if the source is valid, False otherwise.
    """
    # Check title for Zacks and other spammy keywords
    title = article.get('title', '').lower()
    if 'zacks' in title or 'zack' in title:
        return False
        
    # Check publisher/source
    publisher = article.get('publisher', '').lower()
    source = article.get('source', '').lower()
    
    if 'zacks' in publisher or 'zacks' in source:
        return False
        
    # Check recency
    if not is_recent(article.get('published')):
        return False
        
    return True

def get_yahoo_news(ticker: str):
    """Fetches news from Yahoo Finance and filters for relevance."""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        articles = []
        
        # Get company name for filtering (simple heuristic)
        # We might not have the full name easily without an extra API call, 
        # but the ticker is a good start.
        keywords = [ticker.upper()]
        
        for item in news:
            # Handle nested content structure (new yfinance API)
            content = item.get('content', {})
            
            # Try to get title from content or top level
            title = content.get('title') or item.get('title', '')
            
            # Try to get URL
            url = item.get('link')
            if not url:
                url = item.get('clickThroughUrl', {}).get('url')
            if not url:
                url = content.get('canonicalUrl', {}).get('url')
            if not url:
                url = item.get('canonicalUrl', {}).get('url')
                
            # Try to get date
            pub_date = content.get('pubDate') or item.get('providerPublishTime')
            
            # Filter: Title must contain ticker or be very relevant
            # Yahoo Finance usually returns relevant news, so we'll trust it more
            # but still filter out obvious noise if needed later.
            # For now, we return everything yfinance gives us for the ticker.

            if url and title:
                article_data = {
                    'title': title,
                    'url': url,
                    'publisher': item.get('provider', {}).get('displayName') or item.get('publisher', 'Yahoo Finance'),
                    'published': normalize_date(pub_date),
                    'source': 'Yahoo Finance'
                }
                
                if is_valid_source(article_data):
                    articles.append(article_data)
                    
        return articles
    except Exception as e:
        logger.error(f"Error fetching Yahoo news for {ticker}: {e}")
        return []

def get_google_news(ticker: str, company_name: str = None, period='7d'):
    """Fetches news from Google News using company name for more relevant results."""
    try:
        googlenews = GoogleNews(period=period)
        search_term = company_name if company_name else ticker
        googlenews.search(search_term)
        results = googlenews.result()
        articles = []
        for item in results:
            url = item.get('link', '')
            
            # Clean Google News URLs - remove tracking parameters that break links
            if '&ved=' in url:
                url = url.split('&ved=')[0]
            if '&usg=' in url:
                url = url.split('&usg=')[0]
            
            article_data = {
                'title': item.get('title'),
                'url': url,
                'publisher': item.get('media'),
                'published': normalize_date(item.get('date')),
                'source': 'Google News'
            }
            
            if is_valid_source(article_data):
                articles.append(article_data)
                
        return articles
    except Exception as e:
        logger.error(f"Error fetching Google news for {ticker}: {e}")
        return []

def get_finviz_news(ticker: str):
    """Fetches news from FinViz."""
    try:
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        news_table = soup.find(id='news-table')
        if not news_table:
            return []
            
        articles = []
        rows = news_table.findAll('tr')
        
        for row in rows:
            # FinViz format: Date/Time in first td, Link in second td
            cols = row.findAll('td')
            if len(cols) < 2:
                continue
                
            date_str = cols[0].text.strip()
            link_tag = cols[1].find('a')
            
            if not link_tag:
                continue
                
            link = link_tag['href']
            title = link_tag.text
            publisher = "FinViz" # FinViz aggregates, but doesn't always list publisher clearly in the table
            
            # Basic date parsing could be added here if needed
            
            article_data = {
                'title': title,
                'url': link,
                'publisher': publisher,
                'published': normalize_date(date_str),
                'source': 'FinViz'
            }
            
            if is_valid_source(article_data):
                articles.append(article_data)
            
            # Limit to recent news (last 50 items)
            if len(articles) >= 50:
                break
                
        return articles

    except Exception as e:
        logger.error(f"Error fetching FinViz news for {ticker}: {e}")
        return []

def get_article_content(url: str):
    """Downloads and parses article content using newspaper3k."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {e}")
        return None

def get_marketwatch_news(ticker: str, company_name: str = None):
    """Fetches news from MarketWatch by scraping."""
    try:
        search_term = company_name if company_name else ticker
        url = f"https://www.marketwatch.com/search?q={search_term}&ts=0&tab=All%20News"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = []
        # MarketWatch search results - structure may vary
        search_results = soup.find_all('div', class_='article__content')
        
        for result in search_results[:50]:  # Limit to 50
            try:
                link_tag = result.find('a', class_='link')
                if not link_tag:
                    continue
                    
                title = link_tag.get_text(strip=True)
                link = link_tag.get('href')
                
                if not link.startswith('http'):
                    link = 'https://www.marketwatch.com' + link
                
                # Get date if available
                date_tag = result.find('span', class_='article__timestamp')
                date_str = date_tag.get_text(strip=True) if date_tag else None
                
                article_data = {
                    'title': title,
                    'url': link,
                    'publisher': 'MarketWatch',
                    'published': normalize_date(date_str),
                    'source': 'MarketWatch'
                }
                
                if is_valid_source(article_data):
                    articles.append(article_data)
            except Exception as e:
                logger.debug(f"Error parsing MarketWatch result: {e}")
                continue
                
        return articles
    except Exception as e:
        logger.error(f"Error fetching MarketWatch news: {e}")
        return []

def get_benzinga_news(ticker: str):
    """Fetches news from Benzinga by scraping."""
    try:
        url = f"https://www.benzinga.com/quote/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = []
        # Find news items (structure may vary)
        news_items = soup.find_all('div', class_='story-block')
        
        for item in news_items[:50]:  # Limit to 50
            try:
                link_tag = item.find('a')
                if not link_tag:
                    continue
                    
                title = link_tag.get_text(strip=True)
                link = link_tag.get('href')
                
                if not link.startswith('http'):
                    link = 'https://www.benzinga.com' + link
                
                # Get date if available
                date_tag = item.find('time')
                date_str = date_tag.get('datetime') if date_tag else None
                
                article_data = {
                    'title': title,
                    'url': link,
                    'publisher': 'Benzinga',
                    'published': normalize_date(date_str),
                    'source': 'Benzinga'
                }
                
                if is_valid_source(article_data):
                    articles.append(article_data)
            except Exception as e:
                logger.debug(f"Error parsing Benzinga result: {e}")
                continue
                
        return articles
    except Exception as e:
        logger.error(f"Error fetching Benzinga news: {e}")
        return []

def get_reuters_news(ticker: str, company_name: str = None):
    """Fetches news from Reuters by scraping."""
    try:
        search_term = company_name if company_name else ticker
        url = f"https://www.reuters.com/site-search/?query={search_term}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = []
        # Reuters search results structure
        search_results = soup.find_all('div', class_='search-result-indiv')
        
        for result in search_results[:50]:
            try:
                link_tag = result.find('a')
                if not link_tag:
                    continue
                    
                title = link_tag.get_text(strip=True)
                link = link_tag.get('href')
                
                if link and not link.startswith('http'):
                    link = 'https://www.reuters.com' + link
                
                # Get date if available
                date_tag = result.find('time')
                date_str = date_tag.get('datetime') if date_tag else None
                
                article_data = {
                    'title': title,
                    'url': link,
                    'publisher': 'Reuters',
                    'published': normalize_date(date_str),
                    'source': 'Reuters'
                }
                
                if is_valid_source(article_data):
                    articles.append(article_data)
            except Exception as e:
                logger.debug(f"Error parsing Reuters result: {e}")
                continue
                
        return articles
    except Exception as e:
        logger.error(f"Error fetching Reuters news: {e}")
        return []

def get_seekingalpha_news(ticker: str):
    """Fetches news from Seeking Alpha by scraping."""
    try:
        url = f"https://seekingalpha.com/symbol/{ticker}/news"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = []
        # Seeking Alpha article links
        article_links = soup.find_all('a', attrs={'data-test-id': 'post-list-item-title'})
        
        for link_tag in article_links[:50]:
            try:
                title = link_tag.get_text(strip=True)
                link = link_tag.get('href')
                
                if link and not link.startswith('http'):
                    link = 'https://seekingalpha.com' + link
                
                article_data = {
                    'title': title,
                    'url': link,
                    'publisher': 'Seeking Alpha',
                    'published': None,  # Dates are harder to scrape from SA
                    'source': 'Seeking Alpha'
                }
                
                if is_valid_source(article_data):
                    articles.append(article_data)
            except Exception as e:
                logger.debug(f"Error parsing Seeking Alpha result: {e}")
                continue
                
        return articles
    except Exception as e:
        logger.error(f"Error fetching Seeking Alpha news: {e}")
        return []

def get_ir_news(ticker: str, company_name: str = None):
    """
    Attempts to find and scrape news from the company's Investor Relations page.
    Uses Google News with specific IR keywords as a proxy for direct IR scraping,
    which is more robust than trying to find and scrape arbitrary IR websites.
    """
    try:
        search_term = f"{company_name or ticker} Investor Relations press release earnings"
        logger.info(f"Searching for IR news: {search_term}")
        
        googlenews = GoogleNews(period='30d') # Look back 30 days for IR news
        googlenews.search(search_term)
        results = googlenews.result()
        
        articles = []
        
        for item in results:
            url = item.get('link', '')
            
            # Clean Google News URLs
            if '&ved=' in url:
                url = url.split('&ved=')[0]
            if '&usg=' in url:
                url = url.split('&usg=')[0]
            
            article_data = {
                'title': item.get('title'),
                'url': url,
                'publisher': item.get('media') or 'IR Source',
                'published': normalize_date(item.get('date')),
                'source': 'Investor Relations'
            }
            
            if is_valid_source(article_data):
                articles.append(article_data)
                
        return articles

    except Exception as e:
        logger.error(f"Error fetching IR news for {ticker}: {e}")
        return []

def get_aggregated_news(ticker: str):
    """Aggregates news from multiple sources."""
    # Get company name and type first
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        company_name = info.get('longName') or info.get('shortName') or ticker
        quote_type = info.get('quoteType', '').upper()
    except Exception as e:
        logger.warning(f"Error getting info for {ticker}: {e}")
        company_name = ticker
        quote_type = 'UNKNOWN'

    logger.info(f"Fetching news for {ticker} ({company_name}) [Type: {quote_type}]")
    
    # Define types that should use all sources (Stocks/ETFs)
    # Everything else (Crypto, Futures, Indices, etc.) uses only Google News
    STOCK_TYPES = ['EQUITY', 'ETF']
    
    if quote_type in STOCK_TYPES:
        yahoo_news = get_yahoo_news(ticker)
        google_news = get_google_news(ticker, company_name)
        finviz_news = get_finviz_news(ticker)
        marketwatch_news = get_marketwatch_news(ticker, company_name)
        benzinga_news = get_benzinga_news(ticker)
        reuters_news = get_reuters_news(ticker, company_name)
        seekingalpha_news = get_seekingalpha_news(ticker)
        ir_news = get_ir_news(ticker, company_name)
        
        all_news = yahoo_news + google_news + finviz_news + marketwatch_news + benzinga_news + reuters_news + seekingalpha_news + ir_news
    else:
        logger.info(f"Non-stock instrument ({quote_type}), restricting to Google News.")
        # For crypto/futures, Google News with the name is usually best
        all_news = get_google_news(ticker, company_name)
    
    # Deduplicate based on URL
    seen_urls = set()
    unique_news = []
    
    for article in all_news:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_news.append(article)
            
    logger.info(f"Found {len(unique_news)} unique articles for {ticker}")
    return unique_news
