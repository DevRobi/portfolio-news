import requests
import json

BASE_URL = "http://localhost:8000/api/portfolio"

def test_portfolio_api():
    print("1. Getting initial portfolio...")
    res = requests.get(BASE_URL)
    print(f"Initial: {res.json()}")
    
    print("\n2. Adding 'AAPL'...")
    res = requests.post(BASE_URL, json={"ticker": "AAPL"})
    print(f"Add response: {res.json()}")
    
    print("\n3. Verifying 'AAPL' is in portfolio...")
    res = requests.get(BASE_URL)
    portfolio = res.json()['portfolio']
    if "AAPL" in portfolio:
        print("✅ PASS: AAPL added successfully")
    else:
        print("❌ FAIL: AAPL not found")
        
    print("\n4. Removing 'AAPL'...")
    res = requests.delete(f"{BASE_URL}/AAPL")
    print(f"Remove response: {res.json()}")
    
    print("\n5. Verifying 'AAPL' is gone...")
    res = requests.get(BASE_URL)
    portfolio = res.json()['portfolio']
    if "AAPL" not in portfolio:
        print("✅ PASS: AAPL removed successfully")
    else:
        print("❌ FAIL: AAPL still present")

if __name__ == "__main__":
    test_portfolio_api()
