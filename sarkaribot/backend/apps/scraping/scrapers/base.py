"""
Base scraper classes and factory for SarkariBot.

This module provides the foundation for the multi-engine scraping approach,
allowing different scrapers (Scrapy, Playwright, Requests) to be used
based on site requirements.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
import time
import random
from urllib.parse import urljoin, urlparse
import hashlib
import json

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    
    Defines the common interface that all scraping engines must implement.
    """
    
    def __init__(self, source_config: Dict[str, Any]):
        """
        Initialize the scraper with source configuration.
        
        Args:
            source_config: Configuration dictionary for the government source
        """
        self.source_config = source_config
        self.base_url = source_config.get('base_url', '')
        self.delay = source_config.get('request_delay', 2)
        self.max_retries = source_config.get('max_retries', 3)
        self.timeout = source_config.get('timeout', 30)
        self.user_agents = source_config.get('user_agents', [])
        self.scraped_data = []
        self.stats = {
            'pages_scraped': 0,
            'requests_made': 0,
            'items_found': 0,
            'errors': 0
        }
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method to be implemented by subclasses.
        
        Returns:
            List of dictionaries containing scraped job data
        """
        pass
    
    @abstractmethod
    def extract_job_data(self, page_content: str, url: str) -> List[Dict[str, Any]]:
        """
        Extract job data from page content.
        
        Args:
            page_content: HTML content of the page
            url: URL of the page being scraped
            
        Returns:
            List of job data dictionaries
        """
        pass
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent string."""
        if self.user_agents:
            return random.choice(self.user_agents)
        
        # Default user agents if none configured
        default_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        return random.choice(default_agents)
    
    def add_delay(self):
        """Add random delay between requests."""
        delay_time = self.delay + random.uniform(0, 1)
        time.sleep(delay_time)
    
    def generate_content_hash(self, content: str) -> str:
        """
        Generate SHA256 hash of content for duplicate detection.
        
        Args:
            content: Content to hash
            
        Returns:
            SHA256 hash string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = ' '.join(text.split())
        return cleaned.strip()
    
    def resolve_url(self, url: str) -> str:
        """
        Resolve relative URLs to absolute URLs.
        
        Args:
            url: URL to resolve
            
        Returns:
            Absolute URL
        """
        if not url:
            return ""
        
        if url.startswith(('http://', 'https://')):
            return url
        
        return urljoin(self.base_url, url)
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid and accessible.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def get_scraping_headers(self) -> Dict[str, str]:
        """
        Get headers for HTTP requests.
        
        Returns:
            Dictionary of HTTP headers
        """
        return {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def log_error(self, error: str, url: str = ""):
        """
        Log scraping errors.
        
        Args:
            error: Error message
            url: URL where error occurred
        """
        self.stats['errors'] += 1
        logger.error(f"Scraping error for {url}: {error}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get scraping statistics.
        
        Returns:
            Dictionary with scraping stats
        """
        return self.stats.copy()


class ScraperFactory:
    """
    Factory class for creating appropriate scrapers based on source configuration.
    
    Implements the strategy pattern to select the best scraping engine
    for each government website.
    """
    
    @staticmethod
    def create_scraper(source_config: Dict[str, Any]) -> BaseScraper:
        """
        Create appropriate scraper based on source configuration.
        
        Args:
            source_config: Source configuration dictionary
            
        Returns:
            Appropriate scraper instance
            
        Raises:
            ValueError: If scraper type is not supported
        """
        # Determine scraper type based on configuration
        scraper_type = ScraperFactory._determine_scraper_type(source_config)
        
        if scraper_type == 'playwright':
            from .playwright_scraper import PlaywrightScraper
            return PlaywrightScraper(source_config)
        elif scraper_type == 'scrapy':
            from .scrapy_scraper import ScrapyScraper
            return ScrapyScraper(source_config)
        elif scraper_type == 'requests':
            from .requests_scraper import RequestsScraper
            return RequestsScraper(source_config)
        else:
            raise ValueError(f"Unsupported scraper type: {scraper_type}")
    
    @staticmethod
    def _determine_scraper_type(source_config: Dict[str, Any]) -> str:
        """
        Determine the best scraper type for a source.
        
        Args:
            source_config: Source configuration dictionary
            
        Returns:
            Scraper type string ('playwright', 'scrapy', 'requests')
        """
        # Check if explicitly specified
        if 'scraper_type' in source_config:
            return source_config['scraper_type']
        
        # Auto-detect based on site characteristics
        if source_config.get('requires_javascript', False):
            return 'playwright'
        elif source_config.get('complex_structure', False):
            return 'scrapy'
        elif source_config.get('simple_structure', True):
            return 'requests'
        
        # Default to requests for simple sites
        return 'requests'


class DataProcessor:
    """
    Process and validate scraped data before saving to database.
    
    Handles data cleaning, validation, and normalization.
    """
    
    def __init__(self):
        self.required_fields = ['title', 'source_url']
        self.date_fields = ['notification_date', 'application_end_date', 'exam_date']
        self.url_fields = ['application_link', 'notification_pdf', 'source_url']
    
    def process_item(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single scraped item.
        
        Args:
            raw_data: Raw scraped data
            
        Returns:
            Processed and validated data
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        processed_data = {}
        
        # Validate required fields
        for field in self.required_fields:
            if field not in raw_data or not raw_data[field]:
                raise ValueError(f"Required field '{field}' is missing or empty")
        
        # Process each field
        for field, value in raw_data.items():
            if field in self.date_fields:
                processed_data[field] = self._process_date(value)
            elif field in self.url_fields:
                processed_data[field] = self._process_url(value)
            elif isinstance(value, str):
                processed_data[field] = self._clean_text(value)
            else:
                processed_data[field] = value
        
        # Add processing metadata
        processed_data['processed_at'] = time.time()
        processed_data['content_hash'] = self._generate_hash(processed_data)
        
        return processed_data
    
    def _process_date(self, date_value: Any) -> Optional[str]:
        """Process date values into ISO format."""
        if not date_value:
            return None
        
        # Add date parsing logic here
        # This is a simplified version
        return str(date_value)
    
    def _process_url(self, url_value: Any) -> str:
        """Process and validate URL values."""
        if not url_value:
            return ""
        
        url = str(url_value).strip()
        if url and not url.startswith(('http://', 'https://')):
            # Handle relative URLs if needed
            pass
        
        return url
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove HTML tags if present
        import re
        clean_text = re.sub(r'<[^>]+>', ' ', text)
        
        # Normalize whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
    def _generate_hash(self, data: Dict[str, Any]) -> str:
        """Generate hash for duplicate detection."""
        # Create a string representation of key fields
        key_data = {
            'title': data.get('title', ''),
            'source_url': data.get('source_url', ''),
            'notification_date': data.get('notification_date', '')
        }
        
        content_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()


class RateLimiter:
    """
    Rate limiting utility for scraping requests.
    
    Implements various rate limiting strategies to be respectful
    to government websites.
    """
    
    def __init__(self, requests_per_minute: int = 30):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.request_times = []
        self.min_delay = 60.0 / requests_per_minute  # Minimum delay between requests
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        current_time = time.time()
        
        # Remove old requests (older than 1 minute)
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        # Check if we need to wait
        if len(self.request_times) >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.request_times[0]) + 1
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
        
        # Add current request time
        self.request_times.append(current_time)
        
        # Always add minimum delay
        time.sleep(self.min_delay)
