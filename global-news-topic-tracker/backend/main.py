from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import logging
import json
import asyncio
import aiohttp
from typing import AsyncGenerator
from collections import Counter
import re
from typing import Dict, List

# Add country mapping
COUNTRIES = {
    "us": "United States",
    "ar": "Argentina",
    "au": "Australia",
    "bd": "Bangladesh",
    "br": "Brazil",
    "ca": "Canada",
    "ch": "Switzerland",
    "cl": "Chile",
    "cn": "China",
    "co": "Colombia",
    "de": "Germany",
    "eg": "Egypt",
    "es": "Spain",
    "fr": "France",
    "gb": "United Kingdom",
    "id": "Indonesia",
    "il": "Israel",
    "in": "India",
    "it": "Italy",
    "jp": "Japan",
    "kr": "South Korea",
    "mx": "Mexico",
    "my": "Malaysia",
    "ng": "Nigeria",
    "nl": "Netherlands",
    "no": "Norway",
    "nz": "New Zealand",
    "pe": "Peru",
    "ph": "Philippines",
    "pk": "Pakistan",
    "ru": "Russia",
    "sa": "Saudi Arabia",
    "se": "Sweden",
    "sg": "Singapore",
    "za": "South Africa",
    "th": "Thailand",
    "tr": "Turkey",
    "ae": "United Arab Emirates",
    "vn": "Vietnam"
}

# Add language mapping
LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "ml": "Malayalam"  # Add Malayalam
}


app = FastAPI()

# Logging
logger = logging.getLogger("FastAPI")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


class SummarizeRequest(BaseModel):
    texts: list[str]
    model: str = "llama3.2:1b"  # Default to faster model
    stream: bool = False


GOOGLE_NEWS_RSS = "https://news.google.com/rss"

SECTIONS = {
    "world": "headlines/section/topic/WORLD",
    "business": "headlines/section/topic/BUSINESS",
    "technology": "headlines/section/topic/TECHNOLOGY",
    "science": "headlines/section/topic/SCIENCE",
    "sports": "headlines/section/topic/SPORTS",
    "health": "headlines/section/topic/HEALTH"
}

# Optimized models for different use cases
FAST_MODELS = {
    "fastest": "llama3.2:1b",
    "balanced": "llama3.2:3b",
    "quality": "qwen2:7b",
    "tiny": "phi3:mini"
}

# Add endpoint to get available languages
@app.get("/available_languages")
async def get_available_languages():
    """Get list of available languages for news filtering"""
    return {
        "languages": LANGUAGES,
        "default": "en"
    }


@app.get("/news_analytics")
async def get_news_analytics(
        section: str = Query(None),
        query: str = Query(None),
        country: str = Query(None),
        language: str = Query("en"),
        limit: int = Query(50)
):
    """Get analytics data from news headlines"""
    logger.info(f"Generating analytics: section={section}, query={query}, country={country}, language={language}")

    # First, fetch the news
    news_data = await scrape_news(section, query, country, language, limit)

    if "error" in news_data:
        return {"error": news_data["error"]}

    headlines = [item["title"] for item in news_data["headlines"]]
    sources = [item.get("source", "Unknown") for item in news_data["headlines"]]

    # Extract keywords from headlines
    all_text = " ".join(headlines).lower()
    words = re.findall(r'\b[a-z]{4,}\b', all_text)  # Words with 4+ letters
    word_freq = Counter(words).most_common(20)

    # Count sources
    source_freq = Counter(sources).most_common(10)

    # Sentiment analysis (simple approach)
    positive_words = {"good", "great", "excellent", "positive", "success", "win", "growth", "high", "rise", "gain"}
    negative_words = {"bad", "poor", "negative", "crisis", "fall", "drop", "loss", "war", "attack", "death"}

    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    neutral_count = len(words) - positive_count - negative_count

    sentiment = {
        "positive": positive_count,
        "negative": negative_count,
        "neutral": neutral_count
    }

    return {
        "word_frequency": dict(word_freq),
        "source_distribution": dict(source_freq),
        "sentiment": sentiment,
        "total_headlines": len(headlines),
        "country": news_data.get("country", "US"),
        "language": news_data.get("language", "en")
    }

# Update the scrape_news endpoint
@app.get("/scrape_news")
async def scrape_news(
        section: str = Query(None),
        query: str = Query(None),
        country: str = Query(None),
        language: str = Query("en"),  # Add language parameter
        limit: int = Query(10)
):
    logger.info(f"Scraping Google News: section={section}, query={query}, country={country}, language={language}, limit={limit}")

    # Build URL with country and language parameters
    if country and country.lower() in COUNTRIES:
        base_params = f"hl={language}&gl={country}&ceid={country.upper()}:{language}"
    else:
        base_params = f"hl={language}&ceid={language.upper()}:{language}"

    if query:
        url = f"{GOOGLE_NEWS_RSS}/search?q={query}&{base_params}"
    elif section and section.lower() in SECTIONS:
        url = f"{GOOGLE_NEWS_RSS}/{SECTIONS[section.lower()]}?{base_params}"
    else:
        url = f"{GOOGLE_NEWS_RSS}?{base_params}"

    logger.debug(f"Requesting URL: {url}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    logger.error(f"Non-200 response received: {response.status}")
                    return {"headlines": [], "error": f"Failed with {response.status}"}

                text = await response.text()

        soup = BeautifulSoup(text, "xml")
        items = soup.find_all("item")
        logger.debug(f"Found {len(items)} <item> entries in RSS feed")

        headlines = []
        for i, item in enumerate(items[:limit]):
            title = item.title.text if item.title else "No Title"
            link = item.link.text if item.link else ""
            pub_date = item.pubDate.text if item.pubDate else ""
            source = item.source.text if item.source else ""

            headlines.append({
                "title": title,
                "url": link,
                "published": pub_date,
                "source": source
            })

        logger.info(f"Scraped {len(headlines)} headlines successfully.")
        return {
            "headlines": headlines,
            "country": country.upper() if country else "US",
            "country_name": COUNTRIES.get(country.lower(), "United States") if country else "United States",
            "language": language,
            "language_name": LANGUAGES.get(language, "English")
        }

    except Exception as e:
        logger.error(f"Failed to scrape news: {str(e)}", exc_info=True)
        return {"headlines": [], "error": str(e)}


@app.get("/available_countries")
async def get_available_countries():
    """Get list of available countries for news filtering"""
    return {
        "countries": COUNTRIES,
        "default": "us"
    }


async def stream_ollama_response(prompt: str, model: str) -> AsyncGenerator[str, None]:
    """Stream response from Ollama"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "http://localhost:11434/api/generate",
                    json={"model": model, "prompt": prompt, "stream": True},
                    timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'response' in data:
                                yield f"data: {json.dumps({'chunk': data['response']})}\n\n"
                            if data.get('done', False):
                                yield f"data: {json.dumps({'done': True})}\n\n"
                                break
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        logger.error(f"Streaming error: {str(e)}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@app.post("/summarize")
async def summarize(req: SummarizeRequest):
    logger.info(f"Summarizing {len(req.texts)} headlines using model: {req.model}")

    # Optimized prompt for faster processing
    prompt = f"""Summarize these {len(req.texts)} news headlines into comprehensive overview. 
Provide a detailed summary that captures the main themes, events, and trends across all headlines.
Be thorough and insightful:

Headlines:
{chr(10).join(req.texts)}

Summary:"""

    logger.debug(f"Using model: {req.model}")

    if req.stream:
        return StreamingResponse(
            stream_ollama_response(prompt, req.model),
            media_type="text/plain"
        )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "http://localhost:11434/api/generate",
                    json={"model": req.model, "prompt": prompt, "stream": False},
                    timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                result = await response.json()
                summary = result.get("response", "No summary generated")
                logger.info("Summarization complete.")
                return {"summary": summary}

    except Exception as e:
        logger.error(f"Error during summarization: {str(e)}", exc_info=True)
        return {"summary": "Failed to generate summary."}


@app.post("/summarize/fast")
async def summarize_fast(req: SummarizeRequest):
    """Ultra-fast summarization using the smallest model"""
    req.model = FAST_MODELS["fastest"]
    return await summarize(req)


@app.get("/models")
def get_available_models():
    """Get list of recommended models for different use cases"""
    return {
        "fast_models": FAST_MODELS,
        "recommended": {
            "speed_priority": "llama3.2:1b",
            "quality_priority": "qwen2:7b",
            "balanced": "llama3.2:3b"
        }
    }


@app.post("/summarize/batch")
async def summarize_batch(texts: list[str], model: str = "llama3.2:1b"):
    """Process headlines in smaller batches for better performance"""
    batch_size = 5
    batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]

    summaries = []
    for i, batch in enumerate(batches):
        logger.info(f"Processing batch {i + 1}/{len(batches)}")
        prompt = f"Briefly summarize these news headlines:\n{chr(10).join(batch)}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        "http://localhost:11434/api/generate",
                        json={"model": model, "prompt": prompt, "stream": False},
                        timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    result = await response.json()
                    summaries.append(result.get("response", ""))
        except Exception as e:
            logger.error(f"Batch {i + 1} failed: {str(e)}")
            summaries.append(f"Batch {i + 1} failed")

    # Final summary of summaries
    final_prompt = f"Combine these summaries into key global topics:\n{chr(10).join(summaries)}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "http://localhost:11434/api/generate",
                    json={"model": model, "prompt": final_prompt, "stream": False},
                    timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                result = await response.json()
                return {"summary": result.get("response", "Failed to generate final summary")}
    except Exception as e:
        return {"summary": "Failed to generate final summary"}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI server with async optimizations")
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="info")