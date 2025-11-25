from newspaper import Article
import yfinance as yf

def get_news_urls(ticker):
    stock = yf.Ticker(ticker)
    news = stock.news
    return news[0]['content']['canonicalUrl']['url']

url = get_news_urls('BUR')

def get_article_text(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text

print(get_article_text(url))