"""
Custom tools for Phidata agents.
These are callable functions that agents can use.
"""
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from typing import List, Dict
import json
from config import MAX_SEARCH_RESULTS, REQUEST_TIMEOUT
from logger_setup import log


def search_web(query: str, max_results: int = MAX_SEARCH_RESULTS) -> str:
    """
    Search the web using DuckDuckGo.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with title, url, and snippet
    """
    log.info(f"Searching web for: {query}")
    
    try:
        results = []
        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=max_results))
            
        for r in search_results:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", "")
            })
            
        log.info(f"Found {len(results)} search results")
        # Return JSON string so agent tool messages have a `content` string
        return json.dumps(results)
        
    except Exception as e:
        log.error(f"Search failed: {str(e)}")
        return []


def extract_webpage_content(url: str) -> str:
    """
    Extract text content from a webpage.
    
    Args:
        url: URL of the webpage
        
    Returns:
        Extracted text content
    """
    log.info(f"Extracting content from: {url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove unwanted elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        
        # Extract main content
        main = soup.find("main") or soup.find("article") or soup.find("body")
        
        if main:
            text = main.get_text(separator=" ", strip=True)
            # Limit content length
            content = text[:5000]
            log.info(f"Extracted {len(content)} characters")
            return content
        else:
            log.warning("Could not find main content")
            return ""
            
    except Exception as e:
        log.error(f"Content extraction failed: {str(e)}")
        return ""


def analyze_text_statistics(text: str) -> str:
    """
    Analyze basic text statistics.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with word count, sentence count, etc.
    """
    import re
    from collections import Counter
    
    log.info("Analyzing text statistics")
    
    # Basic stats
    words = re.findall(r'\b\w+\b', text.lower())
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Stopwords
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "to", "of", "in", "for", "on",
        "with", "at", "by", "from", "and", "but", "or", "if"
    }
    
    # Keywords
    filtered_words = [w for w in words if w not in stopwords and len(w) > 3]
    keyword_counts = Counter(filtered_words)
    top_keywords = dict(keyword_counts.most_common(15))
    
    stats = {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_sentence_length": round(len(words) / max(len(sentences), 1), 1),
        "top_keywords": top_keywords
    }
    
    log.info(f"Analysis complete: {stats['word_count']} words")
    return json.dumps(stats)


def analyze_sentiment(text: str) -> str:
    """
    Analyze sentiment of text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with sentiment score and label
    """
    from textblob import TextBlob
    
    log.info("Analyzing sentiment")
    
    try:
        # Limit text for performance
        blob = TextBlob(text[:5000])
        score = blob.sentiment.polarity
        
        if score > 0.1:
            label = "positive"
        elif score < -0.1:
            label = "negative"
        else:
            label = "neutral"
        
        result = {
            "score": round(score, 3),
            "label": label
        }
        
        log.info(f"Sentiment: {label} ({score:.2f})")
        return json.dumps(result)
        
    except Exception as e:
        log.error(f"Sentiment analysis failed: {str(e)}")
        return {"score": 0.0, "label": "neutral"}


def create_visualization(keywords: Dict[str, int], sentiment: Dict, topic: str) -> str:
    """
    Create visualization charts.
    
    Args:
        keywords: Dictionary of keywords and their frequencies
        sentiment: Sentiment analysis results
        topic: Research topic
        
    Returns:
        List of paths to generated chart files
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
    from pathlib import Path
    from config import CHARTS_DIR
    
    log.info("Creating visualizations")
    
    Path(CHARTS_DIR).mkdir(parents=True, exist_ok=True)
    chart_paths = []
    
    # 1. Keyword Bar Chart
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        words = list(keywords.keys())[:10]
        counts = list(keywords.values())[:10]
        
        ax.barh(words, counts, color='#4A90D9')
        ax.set_xlabel('Frequency', fontsize=12)
        ax.set_title(f'Top Keywords: {topic}', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        
        plt.tight_layout()
        path = f"{CHARTS_DIR}/keywords.png"
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        chart_paths.append(path)
        log.info(f"Created keyword chart: {path}")
    except Exception as e:
        log.error(f"Keyword chart failed: {e}")
    
    # 2. Word Cloud
    try:
        wc = WordCloud(
            width=800, height=400,
            background_color='white',
            colormap='viridis',
            max_words=50
        ).generate_from_frequencies(keywords)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(f'Word Cloud: {topic}', fontsize=14, fontweight='bold')
        
        path = f"{CHARTS_DIR}/wordcloud.png"
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        chart_paths.append(path)
        log.info(f"Created word cloud: {path}")
    except Exception as e:
        log.error(f"Word cloud failed: {e}")
    
    # 3. Sentiment Gauge
    try:
        fig, ax = plt.subplots(figsize=(8, 4))
        
        score = sentiment.get('score', 0)
        
        # Create gradient background
        colors = ['#E74C3C', '#F39C12', '#2ECC71']
        positions = [-1, 0, 1]
        
        for i, (pos, color) in enumerate(zip(positions, colors)):
            ax.axvspan(pos - 0.5 if i == 0 else positions[i-1], 
                      pos + 0.5 if i == 2 else positions[i+1],
                      alpha=0.3, color=color)
        
        ax.scatter([score], [0.5], s=300, c='#2C3E50', zorder=5, marker='v')
        ax.axvline(x=score, color='#2C3E50', linestyle='--', alpha=0.7)
        
        ax.set_xlim(-1, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel('Sentiment Score', fontsize=12)
        ax.set_title(f'Overall Sentiment: {score:.2f}', fontsize=14, fontweight='bold')
        ax.set_yticks([])
        ax.set_xticks([-1, -0.5, 0, 0.5, 1])
        
        plt.tight_layout()
        path = f"{CHARTS_DIR}/sentiment.png"
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        chart_paths.append(path)
        log.info(f"Created sentiment chart: {path}")
    except Exception as e:
        log.error(f"Sentiment chart failed: {e}")
    
    # Return JSON string of generated chart file paths
    return json.dumps(chart_paths)