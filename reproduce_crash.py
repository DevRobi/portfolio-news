import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from main import get_stock_news

def test_crash():
    print("Testing full pipeline for TOU...")
    try:
        result = get_stock_news("TOU")
        print("Success!")
        print(f"Summary length: {len(result.summary)}")
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_crash()
