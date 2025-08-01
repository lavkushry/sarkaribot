"""
Enhanced SEO Engine with NLTK fallback for SarkariBot.

This provides NLP-powered SEO optimization with graceful degradation
when advanced NLP libraries are not available.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from django.utils.text import slugify
from django.utils.html import strip_tags
from collections import Counter

# Try advanced NLP imports with fallbacks
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
    print("NLTK successfully loaded")
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK not available - using basic text processing")

logger = logging.getLogger(__name__)

# Basic stop words for fallback
BASIC_STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'will', 'with', 'this', 'these', 'they', 'have', 'had',
    'application', 'notification', 'recruitment', 'examination', 'apply'
}

class EnhancedSEOEngine:
    """
    Enhanced SEO engine with multiple NLP backends and graceful fallbacks.
    """
    
    def __init__(self):
        """Initialize the enhanced SEO engine."""
        self.stop_words = self._get_stop_words()
        self.lemmatizer = self._get_lemmatizer()
        
        logger.info(f"SEO Engine initialized - NLTK: {NLTK_AVAILABLE}")
    
    def _get_stop_words(self):
        """Get stop words with fallback."""
        if NLTK_AVAILABLE:
            try:
                return set(stopwords.words('english'))
            except:
                pass
        return BASIC_STOP_WORDS
    
    def _get_lemmatizer(self):
        """Get lemmatizer with fallback."""
        if NLTK_AVAILABLE:
            try:
                return WordNetLemmatizer()
            except:
                pass
        return None
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text using available NLP tools.
        """
        if not text:
            return []
        
        # Clean text
        text = self._clean_text(text)
        
        if NLTK_AVAILABLE:
            return self._extract_keywords_nltk(text, max_keywords)
        else:
            return self._extract_keywords_basic(text, max_keywords)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove HTML tags
        text = strip_tags(text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        return text.lower().strip()
    
    def _extract_keywords_nltk(self, text: str, max_keywords: int) -> List[str]:
        """Extract keywords using NLTK."""
        try:
            # Tokenize
            tokens = word_tokenize(text)
            
            # Remove stop words and short words
            tokens = [
                token for token in tokens 
                if token.lower() not in self.stop_words and len(token) > 2
            ]
            
            # Lemmatize
            if self.lemmatizer:
                tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            
            # Count frequency
            word_freq = Counter(tokens)
            
            # Return most common
            return [word for word, _ in word_freq.most_common(max_keywords)]
            
        except Exception as e:
            logger.warning(f"NLTK keyword extraction failed: {e}")
            return self._extract_keywords_basic(text, max_keywords)
    
    def _extract_keywords_basic(self, text: str, max_keywords: int) -> List[str]:
        """Basic keyword extraction without external libraries."""
        # Split into words
        words = text.split()
        
        # Filter words
        words = [
            word for word in words
            if (
                len(word) > 2 and
                word.lower() not in self.stop_words and
                word.isalpha()
            )
        ]
        
        # Count frequency
        word_freq = Counter(words)
        
        # Return most common
        return [word for word, _ in word_freq.most_common(max_keywords)]
    
    def generate_seo_title(self, job_title: str, department: str = "", year: str = "") -> str:
        """
        Generate SEO-optimized title.
        """
        if not year:
            year = str(datetime.now().year)
        
        # Extract key terms
        keywords = self.extract_keywords(job_title, 3)
        
        # Build title components
        title_parts = []
        
        # Add main job title (truncated)
        main_title = job_title[:40] if len(job_title) > 40 else job_title
        title_parts.append(main_title)
        
        # Add year if not already present
        if year not in job_title:
            title_parts.append(year)
        
        # Add department if provided and space allows
        if department and len(' '.join(title_parts)) < 45:
            title_parts.insert(-1, department)
        
        # Join and add suffix
        title = ' '.join(title_parts)
        title += " - Apply Online | SarkariBot"
        
        # Ensure title is within 60 characters limit
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title
    
    def generate_meta_description(self, job_title: str, total_posts: int = 0, 
                                 last_date: str = "", department: str = "") -> str:
        """
        Generate SEO-optimized meta description.
        """
        # Extract key terms
        keywords = self.extract_keywords(job_title, 2)
        
        # Build description
        desc_parts = []
        
        # Add action phrase
        desc_parts.append("Apply for")
        
        # Add job title (shortened)
        short_title = job_title[:30] if len(job_title) > 30 else job_title
        desc_parts.append(short_title)
        
        # Add posts info
        if total_posts > 0:
            desc_parts.append(f"({total_posts:,} posts)")
        
        # Add department
        if department:
            desc_parts.append(f"in {department}")
        
        # Add deadline
        if last_date:
            desc_parts.append(f"Last date: {last_date}")
        
        # Add call to action
        desc_parts.append("Apply online now!")
        
        description = ' '.join(desc_parts)
        
        # Ensure description is within 160 characters
        if len(description) > 160:
            description = description[:157] + "..."
        
        return description
    
    def generate_structured_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate JSON-LD structured data for job posting.
        """
        structured_data = {
            "@context": "https://schema.org",
            "@type": "JobPosting",
            "title": job_data.get('title', ''),
            "description": job_data.get('description', ''),
            "identifier": {
                "@type": "PropertyValue",
                "name": job_data.get('source_name', 'SarkariBot'),
                "value": str(job_data.get('id', ''))
            },
            "datePosted": job_data.get('notification_date', datetime.now().isoformat()),
            "validThrough": job_data.get('application_end_date', ''),
            "employmentType": "FULL_TIME",
            "hiringOrganization": {
                "@type": "Organization",
                "name": job_data.get('department', job_data.get('source_name', '')),
                "sameAs": job_data.get('source_url', '')
            },
            "jobLocation": {
                "@type": "Place",
                "addressCountry": "IN",
                "addressLocality": "India"
            },
            "baseSalary": {
                "@type": "MonetaryAmount",
                "currency": "INR",
                "value": {
                    "@type": "QuantitativeValue",
                    "value": "As per government norms"
                }
            }
        }
        
        # Add qualification requirements
        if job_data.get('qualification'):
            structured_data["qualifications"] = job_data['qualification']
        
        # Add application URL
        if job_data.get('application_link'):
            structured_data["url"] = job_data['application_link']
        
        return structured_data
    
    def optimize_content(self, content: str) -> str:
        """
        Optimize content for SEO.
        """
        if not content:
            return content
        
        # Extract keywords
        keywords = self.extract_keywords(content, 5)
        
        # Basic content optimization
        # Add keyword density checking and optimization here
        
        return content

# Global instance
seo_engine = EnhancedSEOEngine()
