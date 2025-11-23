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
from datetime import datetime


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
            
            # Extract metadata
            def _meta(name):
                tag = soup.find('meta', attrs={'name': name}) or soup.find('meta', attrs={'property': name})
                if tag:
                    return tag.get('content') or tag.get('value')
                return None

            source.author = _meta('author') or _meta('article:author') or _meta('og:article:author')
            source.publisher = _meta('publisher') or _meta('og:site_name')
            source.publish_date = _meta('article:published_time') or _meta('pubdate') or _meta('date')
            doi_tag = _meta('citation_doi') or _meta('dc.identifier')
            if doi_tag:
                source.doi = doi_tag

            # Extract main content
            main = soup.find("main") or soup.find("article") or soup.find("body")
            
            if main:
                # Get text and clean it
                text = main.get_text(separator=" ", strip=True)
                # Limit content length
                source.content = text[:50000]
                source.accessed_at = datetime.now()
                # Save raw content for provenance
                from pathlib import Path
                from config import OUTPUT_DIR
                raw_dir = Path(OUTPUT_DIR) / 'raw'
                raw_dir.mkdir(parents=True, exist_ok=True)
                import hashlib
                h = hashlib.sha1(source.url.encode('utf-8')).hexdigest()[:10]
                raw_path = raw_dir / f"{h}.txt"
                try:
                    raw_path.write_text(source.content, encoding='utf-8')
                    source.raw_path = str(raw_path)
                except Exception:
                    source.raw_path = None
                log.debug(f"Extracted {len(source.content)} chars from {source.url}")
            else:
                source.content = source.snippet
                log.warning(f"Could not find main content, using snippet")
                source.accessed_at = datetime.now()
                
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
