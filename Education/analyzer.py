"""
Text Analysis module for statistics, keyword extraction, and sentiment analysis.
"""
import re
from collections import Counter
from pathlib import Path
from typing import List
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from textblob import TextBlob
from wordcloud import WordCloud
from models import Source, AnalysisResult
from config import CHARTS_DIR
from logger_setup import log


class TextAnalyzer:
    """Performs text analysis on collected content."""
    
    def __init__(self):
        Path(CHARTS_DIR).mkdir(parents=True, exist_ok=True)
        self.stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "as", "into", "through",
            "during", "before", "after", "above", "below", "between", "under",
            "again", "further", "then", "once", "here", "there", "when",
            "where", "why", "how", "all", "each", "few", "more", "most",
            "other", "some", "such", "no", "nor", "not", "only", "own",
            "same", "so", "than", "too", "very", "just", "and", "but",
            "if", "or", "because", "until", "while", "this", "that", "these",
            "those", "it", "its", "they", "them", "their", "what", "which"
        }
        log.info("TextAnalyzer initialized")
    
    def analyze(self, sources: List[Source], topic: str) -> AnalysisResult:
        """Perform comprehensive text analysis on sources."""
        log.info(f"Analyzing {len(sources)} sources")
        
        # Combine all content
        combined = " ".join([s.content for s in sources])
        
        # Basic stats
        words = re.findall(r'\b\w+\b', combined.lower())
        sentences = re.split(r'[.!?]+', combined)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        word_count = len(words)
        sentence_count = len(sentences)
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        log.debug(f"Stats: {word_count} words, {sentence_count} sentences")
        
        # Keyword extraction
        filtered = [w for w in words if w not in self.stopwords and len(w) > 3]
        keyword_counts = Counter(filtered)
        top_keywords = dict(keyword_counts.most_common(15))
        
        log.debug(f"Top keywords: {list(top_keywords.keys())[:5]}")
        
        # Sentiment analysis
        blob = TextBlob(combined[:5000])  # Limit for performance
        sentiment_score = blob.sentiment.polarity
        
        if sentiment_score > 0.1:
            sentiment_label = "positive"
        elif sentiment_score < -0.1:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
            
        log.debug(f"Sentiment: {sentiment_label} ({sentiment_score:.2f})")
        
        # Generate charts
        chart_paths = self._generate_charts(top_keywords, sentiment_score, topic)
        
        result = AnalysisResult(
            word_count=word_count,
            sentence_count=sentence_count,
            avg_sentence_length=round(avg_sentence_length, 1),
            top_keywords=top_keywords,
            sentiment_score=round(sentiment_score, 3),
            sentiment_label=sentiment_label,
            chart_paths=chart_paths
        )
        
        log.info("Analysis complete")
        return result
    
    def _generate_charts(self, keywords: dict, sentiment: float, topic: str) -> List[str]:
        """Generate visualization charts."""
        chart_paths = []
        
        # 1. Keyword Bar Chart
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            words = list(keywords.keys())[:10]
            counts = list(keywords.values())[:10]
            
            bars = ax.barh(words, counts, color='#4A90D9')
            ax.set_xlabel('Frequency', fontsize=12)
            ax.set_title(f'Top Keywords: {topic}', fontsize=14, fontweight='bold')
            ax.invert_yaxis()
            
            # Add value labels
            for bar, count in zip(bars, counts):
                ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                       str(count), va='center', fontsize=10)
            
            plt.tight_layout()
            path = f"{CHARTS_DIR}/keywords.png"
            plt.savefig(path, dpi=150, bbox_inches='tight')
            plt.close()
            chart_paths.append(path)
            log.debug(f"Generated keyword chart: {path}")
            
        except Exception as e:
            log.error(f"Failed to generate keyword chart: {e}")
        
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
            log.debug(f"Generated word cloud: {path}")
            
        except Exception as e:
            log.error(f"Failed to generate word cloud: {e}")
        
        # 3. Sentiment Gauge
        try:
            fig, ax = plt.subplots(figsize=(8, 4))
            
            # Create gradient background
            colors = ['#E74C3C', '#F39C12', '#2ECC71']
            positions = [-1, 0, 1]
            
            for i, (pos, color) in enumerate(zip(positions, colors)):
                ax.axvspan(pos - 0.5 if i == 0 else positions[i-1], 
                          pos + 0.5 if i == 2 else positions[i+1],
                          alpha=0.3, color=color)
            
            # Plot sentiment marker
            ax.scatter([sentiment], [0.5], s=300, c='#2C3E50', zorder=5, marker='v')
            ax.axvline(x=sentiment, color='#2C3E50', linestyle='--', alpha=0.7)
            
            ax.set_xlim(-1, 1)
            ax.set_ylim(0, 1)
            ax.set_xlabel('Sentiment Score', fontsize=12)
            ax.set_title(f'Overall Sentiment: {sentiment:.2f}', fontsize=14, fontweight='bold')
            ax.set_yticks([])
            ax.set_xticks([-1, -0.5, 0, 0.5, 1])
            ax.set_xticklabels(['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive'])
            
            plt.tight_layout()
            path = f"{CHARTS_DIR}/sentiment.png"
            plt.savefig(path, dpi=150, bbox_inches='tight')
            plt.close()
            chart_paths.append(path)
            log.debug(f"Generated sentiment chart: {path}")
            
        except Exception as e:
            log.error(f"Failed to generate sentiment chart: {e}")
        
        return chart_paths
