"""
Scrapy-based scraper for complex and high-volume scraping.

This module implements a Scrapy-based scraper for handling complex
scraping scenarios with distributed processing capabilities.
"""

from typing import Dict, List, Any, Optional, Generator
import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.http import Request, Response
from scrapy.spiders import Spider
from scrapy.item import Item, Field
from scrapy.pipelines.images import ImagesPipeline
from scrapy.dupefilters import RFPDupeFilter
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.redirect import RedirectMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.robotstxt import RobotsTxtMiddleware
import asyncio
import logging
from datetime import datetime
from .base import BaseScraper
import json
import time

logger = logging.getLogger(__name__)


class JobItem(Item):
    """
    Scrapy Item for job posting data.
    
    Defines the structure of scraped job data.
    """
    # Core fields
    title = Field()
    description = Field()
    url = Field()
    source_url = Field()
    
    # Job details
    department = Field()
    posts = Field()
    qualification = Field()
    
    # Dates
    notification_date = Field()
    last_date = Field()
    exam_date = Field()
    
    # Financial information
    fee = Field()
    salary = Field()
    
    # Eligibility
    age_limit = Field()
    location = Field()
    
    # Links
    apply_link = Field()
    notification_pdf = Field()
    
    # Metadata
    scraped_at = Field()
    scraper_version = Field()


class CustomUserAgentMiddleware(UserAgentMiddleware):
    """
    Custom User-Agent middleware for government websites.
    
    Rotates through realistic user agents to avoid detection.
    """
    
    def __init__(self):
        self.user_agent_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        ]
        self.current_index = 0
    
    def process_request(self, request, spider):
        """Set a rotating user agent for each request."""
        ua = self.user_agent_list[self.current_index % len(self.user_agent_list)]
        request.headers.setdefault(b'User-Agent', ua.encode())
        self.current_index += 1


class CustomRetryMiddleware(RetryMiddleware):
    """
    Custom retry middleware with exponential backoff.
    
    Implements intelligent retry logic for failed requests.
    """
    
    def __init__(self, settings):
        super().__init__(settings)
        self.retry_times = settings.getint('RETRY_TIMES', 3)
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST', -1)
    
    def process_response(self, request, response, spider):
        """Process response and determine if retry is needed."""
        if request.meta.get('dont_retry', False):
            return response
        
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        
        return response
    
    def _retry(self, request, reason, spider):
        """Retry request with exponential backoff."""
        retries = request.meta.get('retry_times', 0) + 1
        
        if retries <= self.retry_times:
            # Exponential backoff: 1s, 2s, 4s, 8s, etc.
            delay = 2 ** (retries - 1)
            
            logger.info(f"Retrying {request.url} (attempt {retries}/{self.retry_times}) "
                       f"after {delay}s delay. Reason: {reason}")
            
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust
            
            # Add delay
            retryreq.meta['download_delay'] = delay
            
            return retryreq
        else:
            logger.error(f"Gave up retrying {request.url} (failed {retries} times): {reason}")


class DataValidationPipeline:
    """
    Pipeline for validating and cleaning scraped data.
    
    Ensures data quality before storing items.
    """
    
    def __init__(self):
        self.processed_count = 0
        self.dropped_count = 0
    
    def process_item(self, item, spider):
        """
        Process and validate a scraped item.
        
        Args:
            item: Scraped item
            spider: Spider instance
            
        Returns:
            Processed item or raises DropItem
        """
        from scrapy.exceptions import DropItem
        
        # Validate required fields
        if not item.get('title'):
            raise DropItem(f"Missing title in {item}")
        
        if not item.get('url'):
            raise DropItem(f"Missing URL in {item}")
        
        # Clean and normalize data
        item['title'] = self._clean_text(item.get('title', ''))
        item['description'] = self._clean_text(item.get('description', ''))
        
        # Add metadata
        item['scraped_at'] = datetime.now().isoformat()
        item['scraper_version'] = '1.0'
        
        # Validate cleaned data
        if len(item['title']) < 10:
            raise DropItem(f"Title too short: {item['title']}")
        
        self.processed_count += 1
        logger.debug(f"Processed item: {item['title'][:50]}...")
        
        return item
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ''
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common prefixes
        prefixes = ['recruitment for', 'notification for', 'vacancy for']
        text_lower = text.lower()
        
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        
        return text
    
    def close_spider(self, spider):
        """Log statistics when spider closes."""
        logger.info(f"Data validation pipeline: {self.processed_count} processed, "
                   f"{self.dropped_count} dropped")


class GovernmentJobSpider(Spider):
    """
    Scrapy spider for government job websites.
    
    Handles the actual scraping logic for job postings.
    """
    
    name = 'government_jobs'
    
    def __init__(self, config: Dict[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.base_url = config.get('base_url', '')
        self.allowed_domains = [self._extract_domain(self.base_url)]
        self.start_urls = [self.base_url]
        
        # Scraping configuration
        self.selectors = config.get('selectors', {})
        self.pagination = config.get('pagination', {})
        self.max_pages = config.get('max_pages', 10)
        
        # Statistics
        self.stats = {
            'pages_scraped': 0,
            'items_found': 0,
            'requests_made': 0,
            'errors': 0,
            'start_time': time.time()
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        return urlparse(url).netloc
    
    def start_requests(self):
        """Generate initial requests."""
        for url in self.start_urls:
            yield Request(
                url=url,
                callback=self.parse,
                meta={'page_number': 1},
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            )
            self.stats['requests_made'] += 1
    
    def parse(self, response: Response) -> Generator:
        """
        Parse the main page and extract job listings.
        
        Args:
            response: Scrapy response object
            
        Yields:
            Requests for job detail pages and pagination
        """
        self.stats['pages_scraped'] += 1
        page_number = response.meta.get('page_number', 1)
        
        logger.info(f"Parsing page {page_number}: {response.url}")
        
        # Extract job links using configured selectors
        job_links = self._extract_job_links(response)
        
        for link in job_links:
            if link:
                absolute_url = response.urljoin(link)
                yield Request(
                    url=absolute_url,
                    callback=self.parse_job,
                    meta={'source_url': response.url}
                )
                self.stats['requests_made'] += 1
        
        # Handle pagination
        if page_number < self.max_pages:
            next_page_url = self._get_next_page_url(response, page_number)
            if next_page_url:
                yield Request(
                    url=next_page_url,
                    callback=self.parse,
                    meta={'page_number': page_number + 1}
                )
                self.stats['requests_made'] += 1
    
    def parse_job(self, response: Response) -> JobItem:
        """
        Parse individual job posting page.
        
        Args:
            response: Scrapy response object
            
        Returns:
            JobItem with extracted data
        """
        logger.debug(f"Parsing job: {response.url}")
        
        item = JobItem()
        
        try:
            # Extract data using configured selectors
            item['title'] = self._extract_text(response, 'title')
            item['description'] = self._extract_text(response, 'description')
            item['department'] = self._extract_text(response, 'department')
            item['posts'] = self._extract_text(response, 'posts')
            item['qualification'] = self._extract_text(response, 'qualification')
            item['notification_date'] = self._extract_text(response, 'notification_date')
            item['last_date'] = self._extract_text(response, 'last_date')
            item['exam_date'] = self._extract_text(response, 'exam_date')
            item['fee'] = self._extract_text(response, 'fee')
            item['salary'] = self._extract_text(response, 'salary')
            item['age_limit'] = self._extract_text(response, 'age_limit')
            item['location'] = self._extract_text(response, 'location')
            
            # Extract links
            item['apply_link'] = self._extract_link(response, 'apply_link')
            item['notification_pdf'] = self._extract_link(response, 'notification_pdf')
            
            # Set URLs
            item['url'] = response.url
            item['source_url'] = response.meta.get('source_url', response.url)
            
            self.stats['items_found'] += 1
            
            return item
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Error parsing job {response.url}: {e}")
            return None
    
    def _extract_job_links(self, response: Response) -> List[str]:
        """Extract job detail page links from listing page."""
        links = []
        
        # Get job link selector from configuration
        link_selector = self.selectors.get('job_links', 'a[href*="job"]::attr(href)')
        
        try:
            if link_selector.startswith('//'):
                # XPath selector
                links = response.xpath(link_selector).getall()
            else:
                # CSS selector
                links = response.css(link_selector).getall()
        except Exception as e:
            logger.error(f"Error extracting job links: {e}")
        
        return links
    
    def _extract_text(self, response: Response, field_name: str) -> str:
        """Extract text content using configured selector."""
        selector = self.selectors.get(field_name, '')
        if not selector:
            return ''
        
        try:
            if selector.startswith('//'):
                # XPath selector
                texts = response.xpath(selector).getall()
            else:
                # CSS selector
                texts = response.css(selector).getall()
            
            # Join multiple text nodes and clean
            text = ' '.join(texts).strip()
            return ' '.join(text.split())  # Normalize whitespace
            
        except Exception as e:
            logger.debug(f"Error extracting {field_name}: {e}")
            return ''
    
    def _extract_link(self, response: Response, field_name: str) -> str:
        """Extract link URL using configured selector."""
        selector = self.selectors.get(field_name, '')
        if not selector:
            return ''
        
        try:
            if selector.startswith('//'):
                # XPath selector for href attribute
                if '/@href' not in selector:
                    selector += '/@href'
                links = response.xpath(selector).getall()
            else:
                # CSS selector for href attribute
                if '::attr(href)' not in selector:
                    selector += '::attr(href)'
                links = response.css(selector).getall()
            
            if links:
                # Return absolute URL
                return response.urljoin(links[0])
            
        except Exception as e:
            logger.debug(f"Error extracting {field_name} link: {e}")
        
        return ''
    
    def _get_next_page_url(self, response: Response, current_page: int) -> Optional[str]:
        """Get URL for next page of results."""
        pagination_config = self.pagination
        
        if not pagination_config:
            return None
        
        # Try different pagination strategies
        if 'next_page_selector' in pagination_config:
            # Use next page link selector
            selector = pagination_config['next_page_selector']
            try:
                if selector.startswith('//'):
                    next_links = response.xpath(selector).getall()
                else:
                    next_links = response.css(selector).getall()
                
                if next_links:
                    return response.urljoin(next_links[0])
            except Exception as e:
                logger.debug(f"Error getting next page link: {e}")
        
        elif 'url_pattern' in pagination_config:
            # Use URL pattern with page number
            pattern = pagination_config['url_pattern']
            try:
                next_page_url = pattern.format(page=current_page + 1)
                return response.urljoin(next_page_url)
            except Exception as e:
                logger.debug(f"Error generating next page URL: {e}")
        
        return None
    
    def closed(self, reason):
        """Called when spider is closed."""
        end_time = time.time()
        duration = end_time - self.stats['start_time']
        
        logger.info(f"Spider closed: {reason}")
        logger.info(f"Statistics: {self.stats}")
        logger.info(f"Duration: {duration:.2f} seconds")


class ScrapyScraper(BaseScraper):
    """
    Scrapy-based scraper for complex scraping scenarios.
    
    Uses the Scrapy framework for robust, scalable web scraping
    with built-in features like request/response middleware,
    item pipelines, and distributed crawling capabilities.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Scrapy scraper.
        
        Args:
            config: Scraper configuration dictionary
        """
        super().__init__(config)
        self.scraped_items = []
        self.spider_stats = {}
        
        # Configure Scrapy settings
        self.scrapy_settings = self._get_scrapy_settings()
    
    def _get_scrapy_settings(self) -> Dict[str, Any]:
        """
        Get Scrapy settings configuration.
        
        Returns:
            Dictionary of Scrapy settings
        """
        settings = {
            # Basic settings
            'USER_AGENT': self.config.get('user_agent', 
                'SarkariBot/1.0 (+https://sarkaribot.com)'),
            'ROBOTSTXT_OBEY': self.config.get('obey_robots_txt', False),
            'CONCURRENT_REQUESTS': self.config.get('concurrent_requests', 8),
            'CONCURRENT_REQUESTS_PER_DOMAIN': self.config.get('concurrent_requests_per_domain', 4),
            
            # Delays and timeouts
            'DOWNLOAD_DELAY': self.config.get('download_delay', 1),
            'RANDOMIZE_DOWNLOAD_DELAY': self.config.get('randomize_delay', True),
            'DOWNLOAD_TIMEOUT': self.config.get('timeout', 30),
            
            # Retry settings
            'RETRY_TIMES': self.config.get('max_retries', 3),
            'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],
            
            # AutoThrottle for adaptive delays
            'AUTOTHROTTLE_ENABLED': True,
            'AUTOTHROTTLE_START_DELAY': 1,
            'AUTOTHROTTLE_MAX_DELAY': 10,
            'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
            'AUTOTHROTTLE_DEBUG': False,
            
            # Middleware
            'DOWNLOADER_MIDDLEWARES': {
                'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
                f'{__name__}.CustomUserAgentMiddleware': 400,
                f'{__name__}.CustomRetryMiddleware': 550,
            },
            
            # Pipelines
            'ITEM_PIPELINES': {
                f'{__name__}.DataValidationPipeline': 300,
            },
            
            # Memory optimization
            'MEMDEBUG_ENABLED': False,
            'REACTOR_THREADPOOL_MAXSIZE': 20,
            
            # Compression
            'COMPRESSION_ENABLED': True,
            
            # Cookies
            'COOKIES_ENABLED': True,
            
            # Logging
            'LOG_LEVEL': 'INFO',
            'LOG_ENABLED': True,
        }
        
        # Add proxy settings if configured
        if self.config.get('proxy'):
            settings['DOWNLOADER_MIDDLEWARES'].update({
                'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110
            })
        
        return settings
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """
        Perform scraping using Scrapy framework.
        
        Returns:
            List of scraped data dictionaries
        """
        logger.info(f"Starting Scrapy scraping for {self.config.get('base_url')}")
        
        try:
            # Set up Scrapy process
            process = CrawlerProcess(self.scrapy_settings)
            
            # Configure spider
            spider_kwargs = {
                'config': self.config,
            }
            
            # Add signal handlers
            crawler = process.create_crawler(GovernmentJobSpider, **spider_kwargs)
            crawler.signals.connect(self._spider_opened, signal=signals.spider_opened)
            crawler.signals.connect(self._spider_closed, signal=signals.spider_closed)
            crawler.signals.connect(self._item_scraped, signal=signals.item_scraped)
            
            # Start crawling
            deferred = process.crawl(crawler)
            process.start()  # This blocks until crawling is finished
            
            logger.info(f"Scrapy scraping completed. Found {len(self.scraped_items)} items")
            return self.scraped_items
            
        except Exception as e:
            logger.error(f"Scrapy scraping failed: {e}")
            self.stats['errors'] += 1
            raise
    
    def _spider_opened(self, spider):
        """Handle spider opened signal."""
        logger.info(f"Spider opened: {spider.name}")
        self.stats['start_time'] = time.time()
    
    def _spider_closed(self, spider, reason):
        """Handle spider closed signal."""
        logger.info(f"Spider closed: {spider.name}, reason: {reason}")
        
        # Update statistics
        self.stats.update(spider.stats)
        self.stats['end_time'] = time.time()
        self.stats['duration'] = self.stats['end_time'] - self.stats['start_time']
        
        # Calculate averages
        if self.stats.get('requests_made', 0) > 0:
            self.stats['average_response_time'] = (
                self.stats.get('total_response_time', 0) / self.stats['requests_made']
            )
    
    def _item_scraped(self, item, response, spider):
        """Handle item scraped signal."""
        # Convert Scrapy item to dictionary
        item_dict = dict(item)
        self.scraped_items.append(item_dict)
        
        logger.debug(f"Item scraped: {item_dict.get('title', 'Unknown')[:50]}...")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get scraping statistics.
        
        Returns:
            Dictionary containing scraping statistics
        """
        return {
            'pages_scraped': self.stats.get('pages_scraped', 0),
            'items_found': len(self.scraped_items),
            'requests_made': self.stats.get('requests_made', 0),
            'errors': self.stats.get('errors', 0),
            'duration': self.stats.get('duration', 0),
            'average_response_time': self.stats.get('average_response_time', 0),
        }
    
    def cleanup(self) -> None:
        """
        Clean up resources after scraping.
        """
        logger.info("Cleaning up Scrapy scraper resources")
        self.scraped_items.clear()
        self.stats.clear()


def response_status_message(status_code: int) -> str:
    """Get human-readable message for HTTP status code."""
    messages = {
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        429: 'Too Many Requests',
        500: 'Internal Server Error',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Timeout',
    }
    return messages.get(status_code, f'HTTP {status_code}')
