"""
Multi-Engine Web Scraping System for SarkariBot.

Implements comprehensive web scraping using multiple engines:
- Requests + BeautifulSoup for simple sites
- Playwright for JavaScript-heavy sites  
- Scrapy for complex crawling operations

According to Knowledge.md specifications for intelligent source handling.
"""

import asyncio
import hashlib
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from urllib.parse import urljoin, urlparse

# Core imports
from django.conf import settings
from django.utils import timezone

# Third-party imports
import requests
from bs4 import BeautifulSoup, Tag
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Playwright imports (with fallback)
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Scrapy imports (with fallback) 
try:
    import scrapy
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    SCRAPY_AVAILABLE = True
except ImportError:
    SCRAPY_AVAILABLE = False

# Internal imports
from .models import ScrapeLog, ScrapedData, ScrapingError, ProxyConfiguration
from apps.sources.models import GovernmentSource
from apps.core.utils import clean_html_text, extract_dates, normalize_text

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for all scraping engines.
    
    Defines the common interface and shared functionality
    for different scraping implementations.
    """
    
    def __init__(self, source: GovernmentSource, config: Dict[str, Any]):
        """
        Initialize the scraper.
        
        Args:
            source: GovernmentSource model instance
            config: Scraping configuration dictionary
        """
        self.source = source
        self.config = config
        self.scrape_log = None
        self.session = None
        
        # Performance tracking
        self.start_time = None
        self.pages_scraped = 0
        self.requests_made = 0
        self.response_times = []
        self.errors = []
        
        # Data storage
        self.scraped_items = []
        
        # Configuration
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        ]
        
        self.delay_between_requests = config.get('delay', 1.0)
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 3)
    
    def create_scrape_log(self) -> ScrapeLog:
        """Create and return a new scrape log."""
        self.scrape_log = ScrapeLog.objects.create(
            source=self.source,
            config_snapshot=self.config,
            scraper_engine=self.get_engine_name()
        )
        return self.scrape_log
    
    @abstractmethod
    def get_engine_name(self) -> str:
        """Return the name of the scraping engine."""
        pass
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Perform the actual scraping operation.
        
        Returns:
            List of scraped job data dictionaries
        """
        pass
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate MD5 hash of content for duplicate detection."""
        return hashlib.md5(content.encode()).hexdigest()
    
    def save_scraped_item(self, data: Dict[str, Any], source_url: str) -> ScrapedData:
        """
        Save a scraped item to the database.
        
        Args:
            data: Scraped data dictionary
            source_url: URL where the data was scraped from
            
        Returns:
            ScrapedData instance
        """
        # Calculate content hash for duplicate detection
        content_string = str(sorted(data.items()))
        content_hash = self.calculate_content_hash(content_string)
        
        try:
            scraped_data = ScrapedData.objects.create(
                source=self.source,
                scrape_log=self.scrape_log,
                raw_data=data,
                source_url=source_url,
                content_hash=content_hash
            )
            
            # Calculate quality score
            scraped_data.calculate_quality_score()
            scraped_data.save()
            
            logger.debug(f"Saved scraped item: {data.get('title', 'Unknown')}")
            return scraped_data
            
        except Exception as e:
            logger.error(f"Error saving scraped item: {e}")
            self.log_error('validation', str(e), source_url)
            return None
    
    def log_error(self, error_type: str, message: str, url: str = '', 
                  selector: str = '', stack_trace: str = ''):
        """
        Log an error that occurred during scraping.
        
        Args:
            error_type: Type of error from ScrapingError.ERROR_TYPE_CHOICES
            message: Error message
            url: URL where error occurred
            selector: CSS/XPath selector that failed
            stack_trace: Full stack trace
        """
        if self.scrape_log:
            ScrapingError.objects.create(
                scrape_log=self.scrape_log,
                error_type=error_type,
                error_message=message,
                url=url,
                selector=selector,
                stack_trace=stack_trace
            )
            
            # Update error count in scrape log
            self.scrape_log.error_count += 1
            self.scrape_log.save(update_fields=['error_count'])
    
    def extract_text_by_selector(self, soup: BeautifulSoup, selector: str, 
                                method: str = 'css') -> Optional[str]:
        """
        Extract text using CSS selector or XPath.
        
        Args:
            soup: BeautifulSoup object
            selector: CSS selector or XPath
            method: 'css' or 'xpath'
            
        Returns:
            Extracted text or None
        """
        try:
            if method == 'css':
                element = soup.select_one(selector)
                return clean_html_text(element.get_text()) if element else None
            else:
                # XPath not directly supported in BeautifulSoup
                # Would need lxml for XPath support
                logger.warning(f"XPath not supported in this scraper: {selector}")
                return None
                
        except Exception as e:
            self.log_error('parsing', f"Selector extraction failed: {str(e)}", 
                          selector=selector)
            return None
    
    def clean_and_normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize scraped data.
        
        Args:
            raw_data: Raw scraped data
            
        Returns:
            Cleaned and normalized data
        """
        cleaned_data = {}
        
        for key, value in raw_data.items():
            if value is None:
                continue
                
            if isinstance(value, str):
                # Clean HTML and normalize text
                cleaned_value = clean_html_text(value)
                cleaned_value = normalize_text(cleaned_value)
                
                # Extract dates if the field suggests it contains dates
                if any(date_keyword in key.lower() for date_keyword in 
                      ['date', 'deadline', 'last_date', 'end_date']):
                    extracted_dates = extract_dates(cleaned_value)
                    if extracted_dates:
                        cleaned_value = extracted_dates[0].strftime('%Y-%m-%d')
                
                cleaned_data[key] = cleaned_value
            else:
                cleaned_data[key] = value
        
        return cleaned_data
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get an active proxy configuration."""
        try:
            proxy_config = ProxyConfiguration.objects.filter(
                status='active'
            ).order_by('-success_rate').first()
            
            if proxy_config:
                return {
                    'http': proxy_config.proxy_url,
                    'https': proxy_config.proxy_url
                }
        except Exception as e:
            logger.warning(f"Failed to get proxy configuration: {e}")
        
        return None


class RequestsScraper(BaseScraper):
    """
    Scraper using Requests + BeautifulSoup.
    
    Best for simple websites without heavy JavaScript.
    Fast and efficient for basic HTML scraping.
    """
    
    def get_engine_name(self) -> str:
        return 'requests'
    
    def __init__(self, source: GovernmentSource, config: Dict[str, Any]):
        super().__init__(source, config)
        self.setup_session()
    
    def setup_session(self):
        """Set up the requests session with retries and headers."""
        self.session = requests.Session()
        
        # Configure retries
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            'User-Agent': self.user_agents[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Set proxy if available
        proxy = self.get_proxy()
        if proxy:
            self.session.proxies.update(proxy)
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Perform scraping using Requests + BeautifulSoup.
        
        Returns:
            List of scraped job data
        """
        self.start_time = time.time()
        self.create_scrape_log()
        
        logger.info(f"Starting requests scraping for {self.source.name}")
        
        try:
            # Get selectors from configuration
            selectors = self.config.get('selectors', {})
            pagination = self.config.get('pagination', {})
            
            # Start with base URL
            current_url = self.source.base_url
            page_count = 0
            max_pages = pagination.get('max_pages', 5)
            
            while current_url and page_count < max_pages:
                page_data = self.scrape_page(current_url, selectors)
                self.scraped_items.extend(page_data)
                
                # Get next page URL
                if pagination.get('next_page'):
                    next_url = self.find_next_page(current_url, pagination['next_page'])
                    current_url = next_url
                else:
                    current_url = None
                
                page_count += 1
                
                # Respect rate limiting
                if current_url:
                    time.sleep(self.delay_between_requests)
            
            # Mark scrape as completed
            self.scrape_log.mark_completed({
                'found': len(self.scraped_items),
                'created': 0,  # Will be updated during processing
                'updated': 0,
                'skipped': 0
            })
            
            logger.info(f"Completed scraping {self.source.name}: {len(self.scraped_items)} items")
            return self.scraped_items
            
        except Exception as e:
            error_msg = f"Scraping failed for {self.source.name}: {str(e)}"
            logger.error(error_msg)
            
            if self.scrape_log:
                self.scrape_log.mark_failed(error_msg)
            
            return []
    
    def scrape_page(self, url: str, selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Scrape a single page for job listings.
        
        Args:
            url: URL to scrape
            selectors: Dictionary of CSS selectors
            
        Returns:
            List of job data from this page
        """
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Track response time
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            self.requests_made += 1
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            page_items = []
            
            # Find job listings on the page
            job_containers = self.find_job_containers(soup, selectors)
            
            for container in job_containers:
                job_data = self.extract_job_data(container, selectors, url)
                if job_data:
                    # Clean and normalize the data
                    clean_data = self.clean_and_normalize_data(job_data)
                    
                    # Save to database
                    saved_item = self.save_scraped_item(clean_data, url)
                    if saved_item:
                        page_items.append(clean_data)
            
            self.pages_scraped += 1
            logger.debug(f"Scraped page {url}: {len(page_items)} jobs found")
            
            return page_items
            
        except requests.RequestException as e:
            self.log_error('network', f"Network error scraping {url}: {str(e)}", url)
            return []
        except Exception as e:
            self.log_error('parsing', f"Parse error scraping {url}: {str(e)}", url)
            return []
    
    def find_job_containers(self, soup: BeautifulSoup, 
                           selectors: Dict[str, str]) -> List[Tag]:
        """
        Find job listing containers on the page.
        
        Args:
            soup: BeautifulSoup object
            selectors: CSS selectors configuration
            
        Returns:
            List of job container elements
        """
        container_selector = selectors.get('job_container', '.job-item, .job-listing, .notification-item')
        containers = soup.select(container_selector)
        
        if not containers:
            # Try alternative selectors
            alternative_selectors = [
                'tr:has(a)',  # Table rows with links
                'li:has(a)',  # List items with links
                '.item:has(a)',  # Generic items with links
                'div:has(a[href*="notification"])',  # Divs with notification links
            ]
            
            for alt_selector in alternative_selectors:
                containers = soup.select(alt_selector)
                if containers:
                    break
        
        return containers
    
    def extract_job_data(self, container: Tag, selectors: Dict[str, str], 
                        base_url: str) -> Optional[Dict[str, Any]]:
        """
        Extract job data from a container element.
        
        Args:
            container: BeautifulSoup Tag containing job info
            selectors: CSS selectors for data extraction
            base_url: Base URL for resolving relative links
            
        Returns:
            Dictionary of extracted job data
        """
        job_data = {}
        
        try:
            # Extract title
            title = self.extract_field(container, selectors.get('title', 'a, h2, h3, .title'))
            if not title:
                return None  # Skip items without titles
            
            job_data['title'] = title
            
            # Extract other fields
            field_mappings = {
                'description': selectors.get('description', '.description, .summary, .details'),
                'last_date': selectors.get('last_date', '.last-date, .deadline, .end-date'),
                'notification_date': selectors.get('notification_date', '.notification-date, .published, .date'),
                'department': selectors.get('department', '.department, .organization, .ministry'),
                'posts': selectors.get('posts', '.posts, .vacancies, .positions'),
                'qualification': selectors.get('qualification', '.qualification, .eligibility, .education'),
                'salary': selectors.get('salary', '.salary, .pay, .compensation'),
                'age_limit': selectors.get('age_limit', '.age-limit, .age, .age-criteria'),
                'location': selectors.get('location', '.location, .place, .state'),
            }
            
            for field, selector in field_mappings.items():
                value = self.extract_field(container, selector)
                if value:
                    job_data[field] = value
            
            # Extract links
            link_element = container.select_one('a')
            if link_element and link_element.get('href'):
                job_data['source_url'] = urljoin(base_url, link_element['href'])
            
            # Extract additional metadata
            job_data['scraped_at'] = datetime.now().isoformat()
            job_data['source_name'] = self.source.name
            
            return job_data
            
        except Exception as e:
            logger.warning(f"Error extracting job data: {e}")
            return None
    
    def extract_field(self, container: Tag, selector: str) -> Optional[str]:
        """
        Extract text from a field using CSS selector.
        
        Args:
            container: Container element
            selector: CSS selector
            
        Returns:
            Extracted text or None
        """
        try:
            element = container.select_one(selector)
            if element:
                text = clean_html_text(element.get_text())
                return text if text.strip() else None
        except Exception:
            pass
        
        return None
    
    def find_next_page(self, current_url: str, next_selector: str) -> Optional[str]:
        """
        Find the URL of the next page.
        
        Args:
            current_url: Current page URL
            next_selector: CSS selector for next page link
            
        Returns:
            Next page URL or None
        """
        try:
            response = self.session.get(current_url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            next_element = soup.select_one(next_selector)
            if next_element and next_element.get('href'):
                return urljoin(current_url, next_element['href'])
                
        except Exception as e:
            logger.warning(f"Error finding next page: {e}")
        
        return None


class PlaywrightScraper(BaseScraper):
    """
    Scraper using Playwright for JavaScript-heavy sites.
    
    Handles sites that require JavaScript execution,
    AJAX loading, and complex interactions.
    """
    
    def get_engine_name(self) -> str:
        return 'playwright'
    
    def __init__(self, source: GovernmentSource, config: Dict[str, Any]):
        super().__init__(source, config)
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not available. Install with: pip install playwright")
    
    async def scrape_async(self) -> List[Dict[str, Any]]:
        """
        Async scraping using Playwright.
        
        Returns:
            List of scraped job data
        """
        self.start_time = time.time()
        self.create_scrape_log()
        
        logger.info(f"Starting Playwright scraping for {self.source.name}")
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            try:
                context = await browser.new_context(
                    user_agent=self.user_agents[0],
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = await context.new_page()
                
                # Set timeout
                page.set_default_timeout(self.timeout * 1000)
                
                # Scrape pages
                selectors = self.config.get('selectors', {})
                pagination = self.config.get('pagination', {})
                
                current_url = self.source.base_url
                page_count = 0
                max_pages = pagination.get('max_pages', 5)
                
                while current_url and page_count < max_pages:
                    page_data = await self.scrape_page_async(page, current_url, selectors)
                    self.scraped_items.extend(page_data)
                    
                    # Handle pagination
                    if pagination.get('next_page'):
                        next_url = await self.find_next_page_async(page, pagination['next_page'])
                        current_url = next_url
                    else:
                        current_url = None
                    
                    page_count += 1
                    
                    # Rate limiting
                    if current_url:
                        await asyncio.sleep(self.delay_between_requests)
                
                # Mark scrape as completed
                self.scrape_log.mark_completed({
                    'found': len(self.scraped_items),
                    'created': 0,
                    'updated': 0,
                    'skipped': 0
                })
                
                logger.info(f"Completed Playwright scraping {self.source.name}: {len(self.scraped_items)} items")
                return self.scraped_items
                
            except Exception as e:
                error_msg = f"Playwright scraping failed for {self.source.name}: {str(e)}"
                logger.error(error_msg)
                
                if self.scrape_log:
                    self.scrape_log.mark_failed(error_msg)
                
                return []
            finally:
                await browser.close()
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Synchronous wrapper for async scraping.
        
        Returns:
            List of scraped job data
        """
        return asyncio.run(self.scrape_async())
    
    async def scrape_page_async(self, page, url: str, 
                               selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Scrape a single page using Playwright.
        
        Args:
            page: Playwright page object
            url: URL to scrape
            selectors: CSS selectors configuration
            
        Returns:
            List of job data from this page
        """
        try:
            start_time = time.time()
            await page.goto(url, wait_until='networkidle')
            
            # Wait for content to load
            await asyncio.sleep(2)
            
            # Track response time
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            self.requests_made += 1
            
            # Extract job data
            page_items = []
            
            # Find job containers
            container_selector = selectors.get('job_container', '.job-item, .job-listing, .notification-item')
            
            # Wait for job containers to appear
            try:
                await page.wait_for_selector(container_selector, timeout=10000)
            except:
                logger.warning(f"Job containers not found on {url}")
                return []
            
            # Get all job containers
            containers = await page.query_selector_all(container_selector)
            
            for container in containers:
                job_data = await self.extract_job_data_async(container, selectors, url)
                if job_data:
                    clean_data = self.clean_and_normalize_data(job_data)
                    saved_item = self.save_scraped_item(clean_data, url)
                    if saved_item:
                        page_items.append(clean_data)
            
            self.pages_scraped += 1
            logger.debug(f"Scraped page {url} with Playwright: {len(page_items)} jobs found")
            
            return page_items
            
        except Exception as e:
            self.log_error('javascript', f"Playwright error scraping {url}: {str(e)}", url)
            return []
    
    async def extract_job_data_async(self, container, selectors: Dict[str, str], 
                                    base_url: str) -> Optional[Dict[str, Any]]:
        """
        Extract job data from a container using Playwright.
        
        Args:
            container: Playwright element handle
            selectors: CSS selectors for data extraction
            base_url: Base URL for resolving relative links
            
        Returns:
            Dictionary of extracted job data
        """
        job_data = {}
        
        try:
            # Extract title
            title_element = await container.query_selector(selectors.get('title', 'a, h2, h3, .title'))
            if title_element:
                title = await title_element.inner_text()
                job_data['title'] = clean_html_text(title)
            else:
                return None
            
            # Extract other fields
            field_mappings = {
                'description': selectors.get('description', '.description, .summary, .details'),
                'last_date': selectors.get('last_date', '.last-date, .deadline, .end-date'),
                'notification_date': selectors.get('notification_date', '.notification-date, .published, .date'),
                'department': selectors.get('department', '.department, .organization, .ministry'),
                'posts': selectors.get('posts', '.posts, .vacancies, .positions'),
                'qualification': selectors.get('qualification', '.qualification, .eligibility, .education'),
                'salary': selectors.get('salary', '.salary, .pay, .compensation'),
                'age_limit': selectors.get('age_limit', '.age-limit, .age, .age-criteria'),
                'location': selectors.get('location', '.location, .place, .state'),
            }
            
            for field, selector in field_mappings.items():
                element = await container.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    cleaned_text = clean_html_text(text)
                    if cleaned_text.strip():
                        job_data[field] = cleaned_text
            
            # Extract links
            link_element = await container.query_selector('a')
            if link_element:
                href = await link_element.get_attribute('href')
                if href:
                    job_data['source_url'] = urljoin(base_url, href)
            
            # Add metadata
            job_data['scraped_at'] = datetime.now().isoformat()
            job_data['source_name'] = self.source.name
            
            return job_data
            
        except Exception as e:
            logger.warning(f"Error extracting job data with Playwright: {e}")
            return None
    
    async def find_next_page_async(self, page, next_selector: str) -> Optional[str]:
        """
        Find the next page URL using Playwright.
        
        Args:
            page: Playwright page object
            next_selector: CSS selector for next page link
            
        Returns:
            Next page URL or None
        """
        try:
            next_element = await page.query_selector(next_selector)
            if next_element:
                href = await next_element.get_attribute('href')
                if href:
                    return urljoin(page.url, href)
        except Exception as e:
            logger.warning(f"Error finding next page with Playwright: {e}")
        
        return None


def get_scraper(source: GovernmentSource) -> BaseScraper:
    """
    Factory function to get the appropriate scraper for a source.
    
    Args:
        source: GovernmentSource instance
        
    Returns:
        Appropriate scraper instance
    """
    config = source.config_json
    
    # Determine scraper based on source configuration
    if config.get('requires_js', False) and PLAYWRIGHT_AVAILABLE:
        logger.info(f"Using Playwright scraper for {source.name}")
        return PlaywrightScraper(source, config)
    elif config.get('complex_structure', False) and SCRAPY_AVAILABLE:
        logger.info(f"Using Scrapy scraper for {source.name}")
        # TODO: Implement ScrapyScraper class
        logger.warning("Scrapy scraper not yet implemented, falling back to Requests")
        return RequestsScraper(source, config)
    else:
        logger.info(f"Using Requests scraper for {source.name}")
        return RequestsScraper(source, config)


def scrape_source(source_id: int) -> Dict[str, Any]:
    """
    Main function to scrape a government source.
    
    Args:
        source_id: ID of the GovernmentSource to scrape
        
    Returns:
        Dictionary with scraping results
    """
    try:
        source = GovernmentSource.objects.get(id=source_id)
        logger.info(f"Starting scrape for source: {source.name}")
        
        # Get appropriate scraper
        scraper = get_scraper(source)
        
        # Perform scraping
        scraped_data = scraper.scrape()
        
        # Update source's last scraped time
        source.last_scraped = timezone.now()
        source.save(update_fields=['last_scraped'])
        
        return {
            'success': True,
            'source': source.name,
            'items_scraped': len(scraped_data),
            'scrape_log_id': scraper.scrape_log.id if scraper.scrape_log else None
        }
        
    except GovernmentSource.DoesNotExist:
        error_msg = f"Source with ID {source_id} not found"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}
    
    except Exception as e:
        error_msg = f"Scraping failed for source {source_id}: {str(e)}"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}


def scrape_all_active_sources() -> Dict[str, Any]:
    """
    Scrape all active government sources.
    
    Returns:
        Dictionary with overall scraping results
    """
    active_sources = GovernmentSource.objects.filter(active=True)
    results = []
    
    for source in active_sources:
        result = scrape_source(source.id)
        results.append(result)
        
        # Add delay between sources to be respectful
        time.sleep(5)
    
    successful_scrapes = sum(1 for r in results if r['success'])
    total_items = sum(r.get('items_scraped', 0) for r in results if r['success'])
    
    return {
        'total_sources': len(active_sources),
        'successful_scrapes': successful_scrapes,
        'failed_scrapes': len(active_sources) - successful_scrapes,
        'total_items_scraped': total_items,
        'results': results
    }
