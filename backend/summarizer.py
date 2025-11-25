import os
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from qwen3_7b import generate_with_qwen

logger = logging.getLogger(__name__)

import datetime

def generate_summary(ticker: str, articles_data: List[Dict[str, Any]]) -> str:
    """
    Generates a detailed summary from a list of article data using Qwen (local) or Gemini (fallback).
    
    Args:
        ticker: The stock ticker symbol.
        articles_data: A list of dictionaries, each containing 'content', 'source', 'title'.
        
    Returns:
        A string containing the detailed write-up with citations.
    """
    
    if not articles_data:
        return "No news articles found to summarize."

    # Prepare the prompt with structured content
    combined_text = ""
    for i, article in enumerate(articles_data):
        source = article.get('source', 'Unknown Source')
        title = article.get('title', 'No Title')
        content = article.get('content', '')[:10000]  # Truncate individual articles if too long
        
        combined_text += f"Source: {source}\nTitle: {title}\nContent:\n{content}\n\n---\n\n"
    
    prompt = f"""You are a senior financial analyst preparing a comprehensive market intelligence report for {ticker}. This is NOT a brief summary - this is a detailed, thorough analysis report.
    
TODAY'S DATE: {datetime.date.today().strftime('%B %d, %Y')}
IMPORTANT: Prioritize news from the last 7 days. If an article is older than 30 days, explicitly note it as historical context or ignore it if irrelevant.

MANDATORY LENGTH REQUIREMENT:
MANDATORY LENGTH REQUIREMENT:
MANDATORY LENGTH REQUIREMENT:
Your report MUST be AT LEAST 50 sentences long, and ideally closer to 100 sentences. 
This is a detailed, deep-dive analysis. DO NOT write fewer than 50 sentences under any circumstances.

COUNT YOUR SENTENCES AS YOU WRITE. After every few sentences, pause and count to ensure you're meeting the requirement.

COUNT YOUR SENTENCES AS YOU WRITE. After every few sentences, pause and count to ensure you're meeting the requirement.

STRICT NEGATIVE CONSTRAINT:
1. NO ANALYST OPINIONS: Do not mention analyst recommendations, price targets, "buy/sell" ratings, or "upside potential". These are opinions, not facts. We care about business fundamentals, not speculation.
2. NO SOURCES IN TEXT: Do not list sources or say "According to...". Integrate facts directly.
3. NO ZACKS/SLOP: Do not use any information from Zacks Research or similar low-quality content farms.
4. NO SENTENCE COUNT: Do not state the sentence count in your output.

PHILOSOPHY & TONE:
Adopt the persona of a rational, value-oriented investor (inspired by Charlie Munger). 
Focus on "materially useful" information: cash flows, competitive advantages, risks, legal outcomes, and strategic shifts.
Avoid "financial slop" and noise. If a piece of news is trivial, ignore it.
Your goal is to save the user time by filtering out the noise and presenting only the signal in a high-density, pleasant-to-read format.

STRUCTURE:
Provide a single, cohesive, and extremely detailed narrative summary of the news from the last 30 days.
Weave all relevant information into a flowing, professional report.
Ensure the narrative is logical and transitions smoothly between topics.

CRITICAL WRITING RULES:
- Each sentence must be substantive and detailed, not filler
- Include specific numbers, dates, percentages, dollar amounts
- Write in professional, flowing prose - no bullet points or lists
- NEVER write fewer than 50 total sentences

Here is the news content to analyze:
{combined_text}

Begin your detailed report now (REMEMBER: minimum 50 sentences, target 50-100):"""

    print(f"\n{'='*50}\nGENERATED PROMPT FOR {ticker}\n{'='*50}")
    print(prompt)
    print(f"{'='*50}\n")

    # Try Local LLM first
    try:
        logger.info(f"Attempting to generate summary with Llama 3 for {ticker}")
        qwen_response = generate_with_qwen(prompt, model="llama3:8b")
        
        if qwen_response:
            print(f"\n{'='*50}\nQWEN OUTPUT FOR {ticker}\n{'='*50}")
            print(qwen_response)
            print(f"{'='*50}\n")
            
            logger.info(f"Successfully generated summary with Qwen for {ticker}")
            return qwen_response
        else:
            logger.warning("Qwen returned empty response, falling back to Gemini")
    except Exception as e:
        logger.warning(f"Qwen failed: {e}. Falling back to Gemini")
    
    # Fallback to Gemini if Qwen fails
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        logger.warning("No GEMINI_API_KEY found and Qwen failed. Returning error message.")
        return f"""**Note: Unable to generate summary.**

Qwen (local model) is not available, and no GEMINI_API_KEY was found.

Please either:
1. Start Ollama server: `ollama serve`
2. Set GEMINI_API_KEY environment variable

Recent news for {ticker} suggests active market movements. {len(articles_data)} articles found. Please review the sources below."""

    try:
        logger.info(f"Attempting to generate summary with Gemini for {ticker}")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(prompt)
        logger.info(f"Successfully generated summary with Gemini for {ticker}")
        
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Error generating summary with Gemini: {e}")
        return f"Error generating summary: {str(e)}. Both Qwen and Gemini failed."
