from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging

from news_fetcher import get_aggregated_news, get_article_content
from summarizer import generate_summary
import yfinance as yf
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock News Aggregator API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ArticleModel(BaseModel):
    title: str
    url: str
    publisher: Optional[str] = None
    published: Optional[str] = None
    source: str

class StockSummary(BaseModel):
    ticker: str
    summary: str
    articles: List[ArticleModel]

@app.get("/")
def read_root():
    return {"message": "Stock News Aggregator API is running"}

import json
import os

PORTFOLIO_FILE = "portfolio.json"

# Simple in-memory cache: {ticker: (data, timestamp)}
news_cache = {}
CACHE_DURATION = 3600  # 1 hour

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading portfolio: {e}")
    return ["DHI", "BUR"]  # Default if file doesn't exist or error

def save_portfolio(portfolio_list):
    try:
        with open(PORTFOLIO_FILE, "w") as f:
            json.dump(portfolio_list, f)
    except Exception as e:
        logger.error(f"Error saving portfolio: {e}")

# Load portfolio on startup
portfolio = load_portfolio()

class TickerRequest(BaseModel):
    ticker: str

@app.get("/api/portfolio")
def get_portfolio():
    return {"portfolio": portfolio}

@app.post("/api/portfolio")
def add_ticker(request: TickerRequest):
    ticker = request.ticker.upper()
    
    # Smart Ticker Resolution
    # 1. Check if valid as is
    final_ticker = ticker
    try:
        info = yf.Ticker(ticker).info
        # If it has no quoteType, it might be invalid, but yfinance is tricky.
        # Usually invalid tickers return empty info or raise error.
        if not info or 'quoteType' not in info:
            raise ValueError("Invalid ticker")
    except:
        # 2. Try adding -USD for crypto
        try:
            crypto_ticker = f"{ticker}-USD"
            info = yf.Ticker(crypto_ticker).info
            if info and 'quoteType' in info:
                final_ticker = crypto_ticker
                logger.info(f"Auto-resolved {ticker} to {final_ticker}")
        except:
            # If both fail, keep original and let it fail later or be handled as unknown
            pass

    if final_ticker not in portfolio:
        portfolio.append(final_ticker)
        save_portfolio(portfolio)
        return {"message": f"Added {final_ticker} to portfolio", "portfolio": portfolio}
    return {"message": f"{final_ticker} already in portfolio", "portfolio": portfolio}

@app.delete("/api/portfolio/{ticker}")
def remove_ticker(ticker: str):
    ticker = ticker.upper()
    if ticker in portfolio:
        portfolio.remove(ticker)
        save_portfolio(portfolio)
        return {"message": f"Removed {ticker} from portfolio", "portfolio": portfolio}
    raise HTTPException(status_code=404, detail="Ticker not found")

@app.get("/api/news/{ticker}", response_model=StockSummary)
def get_stock_news(ticker: str):
    # Check cache first
    current_time = time.time()
    if ticker in news_cache:
        cached_data, timestamp = news_cache[ticker]
        if current_time - timestamp < CACHE_DURATION:
            logger.info(f"Serving cached news for {ticker}")
            return cached_data

    logger.info(f"Fetching news for {ticker}")
    
    # 1. Fetch news articles
    articles_data = get_aggregated_news(ticker)
    
    print(f"\n{'='*50}\nSCRAPED NEWS FOR {ticker}\n{'='*50}")
    for i, article in enumerate(articles_data):
        print(f"{i+1}. [{article.get('source')}] {article.get('title')}")
        print(f"   URL: {article.get('url')}")
        print(f"   Date: {article.get('published')}")
    print(f"{'='*50}\n")
    
    if not articles_data:
        return StockSummary(ticker=ticker, summary="No news found.", articles=[])

    # 2. Extract content for summarization (limit to top 5 to save time/tokens)
    articles_for_summary = []
    processed_articles = []
    
    # Process all articles for display
    for article in articles_data:
        article_model = ArticleModel(
            title=article.get('title') or "No Title",
            url=article.get('url') or "",
            publisher=article.get('publisher'),
            published=str(article.get('published')),
            source=article.get('source') or "Unknown"
        )
        processed_articles.append(article_model)
    
    # But only extract content for first 2 for AI summarization (more content for detailed reports)
    for article in articles_data[:2]:
        content = get_article_content(article['url'])
        if content:
            articles_for_summary.append({
                'content': content,
                'source': article.get('source', 'Unknown'),
                'title': article.get('title', 'No Title')
            })
        
    # 3. Generate summary
    summary = generate_summary(ticker, articles_for_summary)
    
    return StockSummary(
        ticker=ticker,
        summary=summary,
        articles=processed_articles
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
