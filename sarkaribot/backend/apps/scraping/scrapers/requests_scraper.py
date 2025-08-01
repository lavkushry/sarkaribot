"""
Requests-based scraper for simple, fast scraping of government websites.

This scraper is used for static HTML sites with predictable structure
that don't require JavaScript execution.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import time
import logging
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base import BaseScraper, RateLimiter

logger = logging.getLogger(__name__)


class RequestsScraper(BaseScraper):
    """
    Requests + BeautifulSoup based scraper for simple government websites.
    
    Features:
    - Fast and lightweight
    - Automatic retry mechanism
    - Rate limiting
    - Session management
    - Proxy support
    """
    
    def __init__(self, source_config: Dict[str, Any]):
        """
        Initialize the requests scraper.
        
        Args:
            source_config: Configuration dictionary for the government source
        """
        super().__init__(source_config)
        
        # Initialize session with retry strategy
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set up rate limiter
        requests_per_minute = source_config.get('requests_per_minute', 30)
        self.rate_limiter = RateLimiter(requests_per_minute)
        
        # Configure session headers
        self.session.headers.update(self.get_scraping_headers())
        
        # Proxy configuration
        self.setup_proxy()
    
    def setup_proxy(self):
        """Set up proxy configuration if available."""
        proxy_config = self.source_config.get('proxy')
        if proxy_config:
            proxies = {
                'http': proxy_config.get('http'),
                'https': proxy_config.get('https')
            }
            self.session.proxies.update(proxies)
            logger.info("Proxy configured for requests scraper")
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method for requests-based scraping.
        
        Returns:
            List of dictionaries containing scraped job data
        """
        try:
            logger.info(f"Starting requests scraping for {self.base_url}")
            
            # Get starting URLs
            start_urls = self.get_start_urls()
            
            for url in start_urls:
                try:
                    self.scrape_page(url)
                except Exception as e:
                    self.log_error(f"Failed to scrape page {url}: {e}", url)
                    continue
            
            logger.info(f"Completed requests scraping. Found {len(self.scraped_data)} items")
            return self.scraped_data
            
        except Exception as e:
            logger.error(f"Requests scraping failed: {e}")
            raise
    
    def get_start_urls(self) -> List[str]:
        """
        Get list of starting URLs to scrape.
        
        Returns:
            List of URLs to start scraping from
        """
        config = self.source_config.get('urls', {})
        start_urls = config.get('start_urls', [self.base_url])
        
        # Handle category-based URLs
        categories = config.get('categories', [])
        for category in categories:
            category_url = urljoin(self.base_url, category.get('path', ''))
            start_urls.append(category_url)
        
        return start_urls
    
    def scrape_page(self, url: str):
        """
        Scrape a single page and extract job data.
        
        Args:
            url: URL of the page to scrape
        """
        try:
            # Apply rate limiting
            self.rate_limiter.wait_if_needed()
            
            # Make request
            response = self.make_request(url)
            if not response:
                return
            
            # Extract job data
            job_data_list = self.extract_job_data(response.text, url)
            self.scraped_data.extend(job_data_list)
            
            # Update statistics
            self.stats['pages_scraped'] += 1
            self.stats['items_found'] += len(job_data_list)
            
            # Handle pagination
            self.handle_pagination(response.text, url)
            
            logger.debug(f"Scraped {len(job_data_list)} jobs from {url}")
            
        except Exception as e:
            self.log_error(f"Error scraping page: {e}", url)
    
    def make_request(self, url: str) -> Optional[requests.Response]:
        """
        Make HTTP request with error handling.
        
        Args:
            url: URL to request
            
        Returns:
            Response object or None if failed
        """
        try:
            # Update user agent for each request
            self.session.headers['User-Agent'] = self.get_random_user_agent()
            
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            self.stats['requests_made'] += 1
            
            # Check for successful response
            if response.status_code == 200:
                logger.debug(f"Successfully fetched: {url}")
                return response
            else:
                logger.warning(f"HTTP {response.status_code} for {url}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.log_error(f"Request failed: {e}", url)
            return None
    
    def extract_job_data(self, html_content: str, url: str) -> List[Dict[str, Any]]:
        """
        Extract job data from HTML content using BeautifulSoup.
        
        Args:
            html_content: HTML content of the page
            url: URL of the page being scraped
            
        Returns:
            List of job data dictionaries
        """
        job_data_list = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            selectors = self.source_config.get('selectors', {})
            
            # Find job containers
            job_containers = self.find_job_containers(soup, selectors)
            
            for container in job_containers:
                try:
                    job_data = self.extract_single_job(container, selectors, url)
                    if job_data and self.validate_job_data(job_data):
                        job_data_list.append(job_data)
                except Exception as e:
                    logger.warning(f"Failed to extract job data: {e}")
                    continue
            
        except Exception as e:
            self.log_error(f"HTML parsing failed: {e}", url)
        
        return job_data_list
    
    def find_job_containers(self, soup: BeautifulSoup, selectors: Dict[str, Any]) -> List:
        """
        Find job containers in the HTML.
        
        Args:
            soup: BeautifulSoup object
            selectors: Selector configuration
            
        Returns:
            List of job container elements
        """
        container_selector = selectors.get('job_container', '.job-item')
        
        if container_selector.startswith('//'):
            # XPath selector (convert to CSS selector if possible)
            # For now, use a fallback CSS selector
            containers = soup.find_all('div', class_='job-item')
        else:
            # CSS selector
            containers = soup.select(container_selector)
        
        return containers
    
    def extract_single_job(
        self, 
        container, 
        selectors: Dict[str, Any], 
        page_url: str
    ) -> Dict[str, Any]:
        """
        Extract data for a single job from its container.
        
        Args:
            container: BeautifulSoup element containing job data
            selectors: Selector configuration
            page_url: URL of the page being scraped
            
        Returns:
            Dictionary with job data
        """
        job_data = {}
        
        # Extract basic fields
        job_data['title'] = self.extract_text_field(container, selectors.get('title'))
        job_data['description'] = self.extract_text_field(container, selectors.get('description'))
        job_data['department'] = self.extract_text_field(container, selectors.get('department'))
        job_data['total_posts'] = self.extract_number_field(container, selectors.get('total_posts'))
        
        # Extract dates
        job_data['notification_date'] = self.extract_date_field(container, selectors.get('notification_date'))
        job_data['application_end_date'] = self.extract_date_field(container, selectors.get('last_date'))
        job_data['exam_date'] = self.extract_date_field(container, selectors.get('exam_date'))
        
        # Extract links
        job_data['application_link'] = self.extract_link_field(container, selectors.get('application_link'))
        job_data['notification_pdf'] = self.extract_link_field(container, selectors.get('notification_pdf'))
        job_data['source_url'] = self.extract_link_field(container, selectors.get('source_url')) or page_url
        
        # Extract financial information
        job_data['application_fee'] = self.extract_currency_field(container, selectors.get('application_fee'))
        job_data['salary_min'] = self.extract_currency_field(container, selectors.get('salary_min'))
        job_data['salary_max'] = self.extract_currency_field(container, selectors.get('salary_max'))
        
        # Extract eligibility
        job_data['qualification'] = self.extract_text_field(container, selectors.get('qualification'))
        job_data['min_age'] = self.extract_number_field(container, selectors.get('min_age'))
        job_data['max_age'] = self.extract_number_field(container, selectors.get('max_age'))
        
        # Add metadata
        job_data['scraped_at'] = time.time()
        job_data['scraper_type'] = 'requests'
        
        return job_data
    
    def extract_text_field(self, container, selector: Optional[str]) -> str:
        """Extract text content using selector."""
        if not selector:
            return ""
        
        try:
            if selector.startswith('//'):
                # XPath - fallback to attribute or text extraction
                element = container.find(text=True)
                return self.clean_text(str(element)) if element else ""
            else:
                # CSS selector
                element = container.select_one(selector)
                return self.clean_text(element.get_text()) if element else ""
        except Exception:
            return ""
    
    def extract_link_field(self, container, selector: Optional[str]) -> str:
        """Extract link URL using selector."""
        if not selector:
            return ""
        
        try:
            if selector.startswith('//'):
                # XPath - find link elements
                links = container.find_all('a', href=True)
                if links:
                    return self.resolve_url(links[0]['href'])
            else:
                # CSS selector
                element = container.select_one(selector)
                if element:
                    href = element.get('href')
                    return self.resolve_url(href) if href else ""
        except Exception:
            return ""
        
        return ""
    
    def extract_number_field(self, container, selector: Optional[str]) -> Optional[int]:
        """Extract numeric value using selector."""
        text = self.extract_text_field(container, selector)
        if not text:
            return None
        
        try:
            # Extract numbers from text
            import re
            numbers = re.findall(r'\d+', text.replace(',', ''))
            return int(numbers[0]) if numbers else None
        except (ValueError, IndexError):
            return None
    
    def extract_date_field(self, container, selector: Optional[str]) -> Optional[str]:
        """Extract date value using selector."""
        text = self.extract_text_field(container, selector)
        if not text:
            return None
        
        # Use the date extraction utility from core
        from apps.core.utils import extract_date_from_text
        date_obj = extract_date_from_text(text)
        return date_obj.strftime('%Y-%m-%d') if date_obj else None
    
    def extract_currency_field(self, container, selector: Optional[str]) -> Optional[float]:
        """Extract currency value using selector."""
        text = self.extract_text_field(container, selector)
        if not text:
            return None
        
        try:
            # Remove currency symbols and extract numbers
            import re
            text = re.sub(r'[₹$€£,]', '', text)
            numbers = re.findall(r'\d+(?:\.\d+)?', text)
            return float(numbers[0]) if numbers else None
        except (ValueError, IndexError):
            return None
    
    def validate_job_data(self, job_data: Dict[str, Any]) -> bool:
        """
        Validate extracted job data.
        
        Args:
            job_data: Extracted job data
            
        Returns:
            True if data is valid, False otherwise
        """
        # Check required fields
        required_fields = ['title', 'source_url']
        
        for field in required_fields:
            if not job_data.get(field):
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate title length
        title = job_data.get('title', '')
        if len(title.strip()) < 10:
            logger.warning(f"Title too short: {title}")
            return False
        
        return True
    
    def handle_pagination(self, html_content: str, current_url: str):
        """
        Handle pagination to scrape multiple pages.
        
        Args:
            html_content: HTML content of current page
            current_url: URL of current page
        """
        try:
            pagination_config = self.source_config.get('pagination', {})
            if not pagination_config:
                return
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find next page link
            next_selector = pagination_config.get('next_page')
            if next_selector:
                if next_selector.startswith('//'):
                    # XPath - find next page link
                    next_links = soup.find_all('a', string=lambda text: text and 'next' in text.lower())
                    if next_links:
                        next_url = next_links[0].get('href')
                        if next_url:
                            next_url = self.resolve_url(next_url)
                            self.scrape_page(next_url)
                else:
                    # CSS selector
                    next_element = soup.select_one(next_selector)
                    if next_element:
                        next_url = next_element.get('href')
                        if next_url:
                            next_url = self.resolve_url(next_url)
                            self.scrape_page(next_url)
            
            # Handle numbered pagination
            max_pages = pagination_config.get('max_pages', 1)
            if max_pages > 1 and self.stats['pages_scraped'] < max_pages:
                # Try to find numbered pagination
                self.handle_numbered_pagination(soup, current_url, max_pages)
                
        except Exception as e:
            logger.warning(f"Pagination handling failed: {e}")
    
    def handle_numbered_pagination(self, soup: BeautifulSoup, current_url: str, max_pages: int):
        """Handle numbered pagination (1, 2, 3, ...)."""
        try:
            # Look for pagination numbers
            page_links = soup.find_all('a', string=lambda text: text and text.isdigit())
            
            for link in page_links:
                page_num = int(link.string)
                if page_num <= max_pages and page_num > self.stats['pages_scraped']:
                    page_url = self.resolve_url(link.get('href'))
                    if page_url and page_url != current_url:
                        self.scrape_page(page_url)
                        break  # Scrape one page at a time
                        
        except Exception as e:
            logger.warning(f"Numbered pagination failed: {e}")
    
    def __del__(self):
        """Clean up session when scraper is destroyed."""
        if hasattr(self, 'session'):
            self.session.close()
