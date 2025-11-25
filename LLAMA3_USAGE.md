# Qwen Model Usage Guide

The `qwen3_7b.py` file has been fixed to work with your local Ollama server running on localhost:11434.

## What was fixed:
1. Changed endpoint from `/v1/complete` to `/api/generate` (Ollama's correct API endpoint)
2. Updated request format to match Ollama's API specification
3. Set default model to `qwen:7b` (the model you have installed)
4. Added proper error handling and connection checks
5. Created reusable `generate_with_qwen()` function

## Usage:

### Basic usage:
```python
from backend.qwen3_7b import generate_with_qwen

prompt = "Summarize this article: ..."
response = generate_with_qwen(prompt)
print(response)
```

### Test the model:
```bash
python backend/qwen3_7b.py
```

### Use with different model (if you have others installed):
```python
response = generate_with_qwen(prompt, model="llama2:7b")
```

## Integration with summarizer:

You can integrate this into your `summarizer.py` as an alternative to Gemini:

```python
from qwen3_7b import generate_with_qwen

def generate_summary_qwen(ticker: str, articles_data: List[Dict[str, Any]]) -> str:
    # Prepare content
    combined_text = ""
    for article in articles_data:
        source = article.get('source', 'Unknown')
        title = article.get('title', 'No Title')
        content = article.get('content', '')[:5000]
        combined_text += f"Source: {source}\nTitle: {title}\nContent:\n{content}\n\n---\n\n"
    
    prompt = f"""You are a financial analyst. Write a detailed paragraph summarizing the latest news for {ticker}.
Focus on the most important events, market sentiment, and any legal or financial developments.
IMPORTANT: Cite your sources (e.g., "According to Yahoo Finance, ...").

{combined_text}

Summary:"""
    
    return generate_with_qwen(prompt)
```

## Notes:
- Make sure Ollama is running (`ollama serve`)
- Your model is `qwen:7b` (Qwen2 8B parameter model, Q4_0 quantized)
- The model runs locally, no API key needed
- Responses are generated on your machine
