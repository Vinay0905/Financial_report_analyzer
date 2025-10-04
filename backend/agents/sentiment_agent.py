import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from backend.config.settings import settings

# Sentiment analysis libraries
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("Warning: vaderSentiment not installed. Using fallback sentiment analysis.")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: textblob not installed. Using fallback sentiment analysis.")

class SentimentAgent:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer() if VADER_AVAILABLE else None
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Financial-Analyzer/1.0'})
        
    def analyze(self, symbol=None, company_name=None):
        """
        Comprehensive sentiment analysis using multiple sources and methods.
        Returns detailed sentiment breakdown with headlines.
        """
        query = symbol or company_name
        if not query:
            return self._empty_sentiment()
        
        print(f"Starting sentiment analysis for: {query}")
        
        # Collect articles from multiple sources
        all_articles = []
        
        # Source 1: NewsAPI
        newsapi_articles = self._get_newsapi_articles(query)
        all_articles.extend(newsapi_articles)
        print(f"NewsAPI returned {len(newsapi_articles)} articles")
        
        # Source 2: Alternative query (company name if we started with symbol)
        if symbol and company_name and len(all_articles) < 10:
            alt_articles = self._get_newsapi_articles(company_name)
            all_articles.extend(alt_articles)
            print(f"Alternative query returned {len(alt_articles)} additional articles")
        
        # Source 3: Google News RSS (as fallback)
        if len(all_articles) < 5:
            rss_articles = self._get_google_news_rss(query)
            all_articles.extend(rss_articles)
            print(f"Google News RSS returned {len(rss_articles)} articles")
        
        # Remove duplicates based on title
        unique_articles = self._remove_duplicates(all_articles)
        print(f"Total unique articles after deduplication: {len(unique_articles)}")
        
        if not unique_articles:
            print("Warning: No articles found for sentiment analysis")
            return self._empty_sentiment()
        
        # Analyze sentiment using multiple methods
        return self._analyze_sentiment(unique_articles)
    
    def _get_newsapi_articles(self, query: str) -> List[Dict]:
        """Get articles from NewsAPI."""
        try:
            # Use last 7 days for better coverage
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': settings.NEWS_API_KEY,
                'from': from_date,
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': 50  # Get more articles
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'ok':
                print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
            
            articles = []
            for article in data.get('articles', []):
                if article.get('title') and article['title'] != '[Removed]':
                    articles.append({
                        'title': article['title'],
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': 'NewsAPI',
                        'publishedAt': article.get('publishedAt', '')
                    })
            
            return articles
            
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return []
    
    def _get_google_news_rss(self, query: str) -> List[Dict]:
        """Get articles from Google News RSS as fallback."""
        try:
            import xml.etree.ElementTree as ET
            
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            articles = []
            
            for item in root.findall('.//item')[:20]:  # Limit to 20 items
                title_elem = item.find('title')
                link_elem = item.find('link')
                pub_date_elem = item.find('pubDate')
                
                if title_elem is not None and title_elem.text:
                    articles.append({
                        'title': title_elem.text,
                        'description': '',
                        'url': link_elem.text if link_elem is not None else '',
                        'source': 'Google News',
                        'publishedAt': pub_date_elem.text if pub_date_elem is not None else ''
                    })
            
            return articles
            
        except Exception as e:
            print(f"Error fetching from Google News RSS: {e}")
            return []
    
    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity."""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title_lower = article['title'].lower().strip()
            # Simple deduplication - could be enhanced with fuzzy matching
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)
        
        return unique_articles
    
    def _analyze_sentiment(self, articles: List[Dict]) -> Dict:
        """Analyze sentiment using multiple methods and combine results."""
        sentiment_data = {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "headlines": [],
            "total_articles": len(articles),
            "sentiment_breakdown": {},
            "confidence_score": 0.0
        }
        
        sentiment_scores = []
        
        for article in articles:
            title = article['title']
            description = article.get('description', '')
            text_to_analyze = f"{title} {description}".strip()
            
            # Method 1: VADER Sentiment (if available)
            vader_score = 0
            if self.vader_analyzer:
                vs = self.vader_analyzer.polarity_scores(text_to_analyze)
                vader_score = vs['compound']
            
            # Method 2: TextBlob Sentiment (if available)
            textblob_score = 0
            if TEXTBLOB_AVAILABLE:
                blob = TextBlob(text_to_analyze)
                textblob_score = blob.sentiment.polarity
            
            # Method 3: Keyword-based sentiment (fallback)
            keyword_score = self._keyword_sentiment(text_to_analyze)
            
            # Combine scores (weighted average)
            combined_score = 0
            weight_sum = 0
            
            if vader_score != 0:
                combined_score += vader_score * 0.4
                weight_sum += 0.4
            
            if textblob_score != 0:
                combined_score += textblob_score * 0.4
                weight_sum += 0.4
            
            combined_score += keyword_score * 0.2
            weight_sum += 0.2
            
            if weight_sum > 0:
                final_score = combined_score / weight_sum
            else:
                final_score = 0
            
            sentiment_scores.append(abs(final_score))  # For confidence calculation
            
            # Classify sentiment
            if final_score > 0.1:
                sentiment_data["positive"] += 1
                sentiment_class = "positive"
            elif final_score < -0.1:
                sentiment_data["negative"] += 1
                sentiment_class = "negative"
            else:
                sentiment_data["neutral"] += 1
                sentiment_class = "neutral"
            
            # Add to headlines with sentiment info
            sentiment_data["headlines"].append({
                "title": title,
                "sentiment": sentiment_class,
                "score": round(final_score, 3),
                "source": article.get('source', 'Unknown'),
                "url": article.get('url', '')
            })
        
        # Calculate overall confidence score
        if sentiment_scores:
            sentiment_data["confidence_score"] = round(sum(sentiment_scores) / len(sentiment_scores), 3)
        
        # Add percentage breakdown
        total = sentiment_data["total_articles"]
        if total > 0:
            sentiment_data["sentiment_breakdown"] = {
                "positive_pct": round((sentiment_data["positive"] / total) * 100, 1),
                "negative_pct": round((sentiment_data["negative"] / total) * 100, 1),
                "neutral_pct": round((sentiment_data["neutral"] / total) * 100, 1)
            }
        
        return sentiment_data
    
    def _keyword_sentiment(self, text: str) -> float:
        """Fallback keyword-based sentiment analysis."""
        positive_words = [
            'gain', 'rise', 'growth', 'profit', 'surge', 'increase', 'strong',
            'beat', 'exceed', 'outperform', 'bullish', 'positive', 'good',
            'success', 'winning', 'record', 'high', 'boost', 'upgrade'
        ]
        
        negative_words = [
            'loss', 'drop', 'decline', 'fall', 'decrease', 'weak', 'miss',
            'underperform', 'bearish', 'negative', 'bad', 'failure', 'losing',
            'low', 'downgrade', 'concern', 'risk', 'trouble', 'lawsuit'
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Normalize based on text length
        total_words = len(text.split())
        if total_words == 0:
            return 0
        
        pos_ratio = positive_count / total_words
        neg_ratio = negative_count / total_words
        
        return pos_ratio - neg_ratio
    
    def _empty_sentiment(self) -> Dict:
        """Return empty sentiment data structure."""
        return {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "headlines": [],
            "total_articles": 0,
            "sentiment_breakdown": {},
            "confidence_score": 0.0
        }
