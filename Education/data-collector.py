"""
Data Collection module for web scraping and content extraction.
Uses DuckDuckGo for free search and BeautifulSoup for extraction.
"""
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from typing import List
from models import Source
from config import MAX_SEARCH_RESULTS, REQUEST_TIMEOUT
from logger_setup import log


class DataCollector:
    """Handles web search and content extraction."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        log.info("DataCollector initialized")
    
    def search(self, query: str, max_results: int = MAX_SEARCH_RESULTS) -> List[Source]:
        """Search for sources using DuckDuckGo."""
        log.info(f"Searching for: {query}")
        sources = []
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                
            for r in results:
                source = Source(
                    url=r.get("href", ""),
                    title=r.get("title", ""),
                    snippet=r.get("body", "")
                )
                sources.append(source)
                log.debug(f"Found source: {source.title[:50]}...")
                
            log.info(f"Found {len(sources)} sources")
            
        except Exception as e:
            log.error(f"Search failed: {str(e)}")
            
        return sources
    
    def extract_content(self, source: Source) -> Source:
        """Extract text content from a URL."""
        log.info(f"Extracting content from: {source.url}")
        
        try:
            response = requests.get(
                source.url, 
                headers=self.headers, 
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove unwanted elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            
            # Extract main content
            main = soup.find("main") or soup.find("article") or soup.find("body")
            
            if main:
                # Get text and clean it
                text = main.get_text(separator=" ", strip=True)
                # Limit content length
                source.content = text[:5000]
                log.debug(f"Extracted {len(source.content)} chars from {source.url}")
            else:
                source.content = source.snippet
                log.warning(f"Could not find main content, using snippet")
                
        except requests.RequestException as e:
            log.error(f"Failed to fetch {source.url}: {str(e)}")
            source.content = source.snippet
            
        except Exception as e:
            log.error(f"Content extraction failed: {str(e)}")
            source.content = source.snippet
            
        return source
    
    def collect_sources(self, query: str, num_sources: int = 3) -> List[Source]:
        """Search and extract content from multiple sources."""
        log.info(f"Collecting {num_sources} sources for: {query}")
        
        # Search for sources
        sources = self.search(query, max_results=num_sources + 2)
        
        # Extract content from top sources
        collected = []
        for source in sources[:num_sources]:
            source = self.extract_content(source)
            if source.content:
                collected.append(source)
                
        log.info(f"Successfully collected {len(collected)} sources")
        return collected
