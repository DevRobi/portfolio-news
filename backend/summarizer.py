import os
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from llama3 import generate_with_llama

logger = logging.getLogger(__name__)

import datetime
import re

def remove_zacks_sentences(text: str) -> str:
    """
    Removes any sentences containing 'Zacks' or 'Zacks Research' from the generated text.
    This is a post-processing step to ensure no Zacks content slips through.
    
    Args:
        text: The generated summary text
        
    Returns:
        Text with Zacks sentences removed
    """
    if not text:
        return text
    
    # Split into sentences (handles common sentence endings)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Filter out sentences containing 'zacks' (case-insensitive)
    filtered_sentences = []
    removed_count = 0
    
    for sentence in sentences:
        if 'zacks' in sentence.lower():
            logger.info(f"Removed Zacks sentence: {sentence[:100]}...")
            removed_count += 1
        else:
            filtered_sentences.append(sentence)
    
    if removed_count > 0:
        logger.warning(f"Post-processing removed {removed_count} sentence(s) containing 'Zacks' content")
    
    # Rejoin sentences
    return ' '.join(filtered_sentences)

def generate_summary(ticker: str, articles_data: List[Dict[str, Any]]) -> str:
    """
    Generates a detailed summary from a list of article data using Llama 3 (local) or Gemini (fallback).
    
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
    valid_article_count = 0
    
    for i, article in enumerate(articles_data):
        source = article.get('source', 'Unknown Source')
        title = article.get('title', 'No Title')
        content = article.get('content', '')[:10000]  # Truncate individual articles if too long
        
        # DOUBLE CHECK: Filter out Zacks if it slipped through
        if 'zacks' in source.lower() or 'zacks' in title.lower() or 'zacks' in content.lower()[:200]: # Check start of content too
            logger.info(f"Skipping Zacks article detected in summarizer: {title}")
            continue
            
        combined_text += f"Source: {source}\nTitle: {title}\nContent:\n{content}\n\n---\n\n"
        valid_article_count += 1
        
    if valid_article_count == 0:
        return "No valid news articles found (filtered out low quality sources)."
    
    prompt = f"""You are a senior financial analyst preparing a comprehensive market intelligence report for {ticker}. This is NOT a brief summary - this is a detailed, thorough analysis report.
    
NEWS SOURCES: The articles below are from Finviz, Yahoo Finance, and Google News.

TODAY'S DATE: {datetime.date.today().strftime('%B %d, %Y')}
IMPORTANT: Prioritize news from the last 7 days. If an article is older than 30 days, explicitly note it as historical context or ignore it if irrelevant.

MANDATORY LENGTH REQUIREMENT:
Aim for 50+ sentences of detailed analysis.
Your report MUST be AT LEAST 50 sentences long.
DO NOT write fewer than 50 sentences.

COUNT YOUR SENTENCES AS YOU WRITE. After every few sentences, pause and count to ensure you're meeting the requirement.


STRICT NEGATIVE CONSTRAINTS:
1. NO ANALYST OPINIONS: Do not mention analyst recommendations, price targets, "buy/sell" ratings, or "upside potential". These are opinions, not facts. We care about business fundamentals, not speculation.

2. NO SOURCES IN TEXT: Do not list sources or say "According to...". Integrate facts directly.

3. ABSOLUTELY NO ZACKS: ZERO TOLERANCE for Zacks Investment Research content. If you encounter ANY information that mentions Zacks, Zacks Research, "Zacks Rank", "Strong Buy" ratings from Zacks, or any Zacks-related terms, IGNORE IT COMPLETELY. Do not use it. Do not reference it. Do not include any sentence that contains the word "Zacks" in any form. This is MANDATORY.

4. TICKER FOCUS ONLY: This report is EXCLUSIVELY about {ticker}. You may BRIEFLY mention competitors or industry dynamics for context (maximum 1-2 sentences per competitor), but DO NOT write lengthy analysis about other companies. If you find yourself writing 3+ sentences about a competitor or devoting an entire paragraph to another company (e.g., American Tower, AMT, or any other ticker), STOP immediately and refocus on {ticker}. The reader only cares about {ticker}.

5. NO SENTENCE COUNT: DO NOT include a sentence count or "Sentence count: X" at the end of the report. Just end with the conclusion.

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
- **NUMBERS HAVE PRIORITY**: Always include specific numbers, dates, percentages, and dollar amounts.
- **METRICS MATTER**: Explicitly mention assets, liabilities, earnings, revenue, and growth/decline percentages whenever available.
- Each sentence must be substantive and detailed, not filler.
- Write in professional, flowing prose - no bullet points or lists.
- NEVER write fewer than 50 total sentences.

Here is the news content to analyze:
{combined_text}

Begin your detailed report now (REMEMBER: minimum 50 sentences, target 50-100):"""

    print(f"\n{'='*50}\nGENERATED PROMPT FOR {ticker}\n{'='*50}")
    print(prompt)
    print(f"{'='*50}\n")

    # Try Local LLM first
    try:
        logger.info(f"Attempting to generate summary with Llama 3 for {ticker}")
        llama_response = generate_with_llama(prompt, model="llama3:8b")
        
        if llama_response:
            print(f"\n{'='*50}\nLLAMA3 OUTPUT FOR {ticker}\n{'='*50}")
            print(llama_response)
            print(f"{'='*50}\n")
            
            # Post-process to remove any Zacks sentences
            cleaned_response = remove_zacks_sentences(llama_response)
            
            logger.info(f"Successfully generated summary with Llama 3 for {ticker}")
            return cleaned_response
        else:
            logger.warning("Llama 3 returned empty response, falling back to Gemini")
    except Exception as e:
        logger.warning(f"Llama 3 failed: {e}. Falling back to Gemini")
    
    # Fallback to Gemini if Llama 3 fails
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        logger.warning("No GEMINI_API_KEY found and Llama 3 failed. Returning error message.")
        return f"""**Note: Unable to generate summary.**

Llama 3 (local model) is not available, and no GEMINI_API_KEY was found.

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
        
        # Post-process to remove any Zacks sentences
        cleaned_response = remove_zacks_sentences(response.text.strip())
        
        return cleaned_response
        
    except Exception as e:
        logger.error(f"Error generating summary with Gemini: {e}")
        return f"Error generating summary: {str(e)}. Both Llama 3 and Gemini failed."
