import yfinance as yf

def check_ticker(ticker):
    print(f"Checking {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        print(f"Long Name: {info.get('longName')}")
        print(f"Short Name: {info.get('shortName')}")
        print(f"Exchange: {info.get('exchange')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_ticker("TOU")
    check_ticker("TOU.TO")
