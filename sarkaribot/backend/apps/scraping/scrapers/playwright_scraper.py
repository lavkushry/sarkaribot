"""
Playwright-based scraper for JavaScript-heavy government websites.

This scraper handles sites that require browser automation, JavaScript execution,
and complex user interactions.
"""

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import asyncio
from typing import Dict, List, Any, Optional
import time
import logging
import json

from .base import BaseScraper, RateLimiter

logger = logging.getLogger(__name__)


class PlaywrightScraper(BaseScraper):
    """
    Playwright-based scraper for JavaScript-heavy government websites.
    
    Features:
    - Full browser automation
    - JavaScript execution
    - Dynamic content handling
    - Screenshot capture for debugging
    - Mobile device emulation
    - Network request interception
    """
    
    def __init__(self, source_config: Dict[str, Any]):
        """
        Initialize the Playwright scraper.
        
        Args:
            source_config: Configuration dictionary for the government source
        """
        super().__init__(source_config)
        
        # Playwright configuration
        self.browser = None
        self.context = None
        self.page = None
        
        # Browser settings
        self.headless = source_config.get('headless', True)
        self.viewport = source_config.get('viewport', {'width': 1920, 'height': 1080})
        self.device_type = source_config.get('device_type', 'desktop')  # desktop, mobile, tablet
        
        # JavaScript and interaction settings
        self.wait_for_selector = source_config.get('wait_for_selector')
        self.wait_timeout = source_config.get('wait_timeout', 30000)  # 30 seconds
        self.enable_screenshots = source_config.get('enable_screenshots', False)
        
        # Rate limiting
        requests_per_minute = source_config.get('requests_per_minute', 20)  # Lower for browser automation
        self.rate_limiter = RateLimiter(requests_per_minute)
        
        # Network settings
        self.block_resources = source_config.get('block_resources', ['image', 'stylesheet', 'font'])
        self.intercept_requests = source_config.get('intercept_requests', False)
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method using Playwright.
        
        Returns:
            List of dictionaries containing scraped job data
        """
        try:
            logger.info(f"Starting Playwright scraping for {self.base_url}")
            
            # Run the async scraping method
            return asyncio.run(self._async_scrape())
            
        except Exception as e:
            logger.error(f"Playwright scraping failed: {e}")
            raise
        finally:
            # Ensure cleanup
            if self.browser:
                asyncio.run(self._cleanup())
    
    async def _async_scrape(self) -> List[Dict[str, Any]]:
        """Async scraping implementation."""
        try:
            # Initialize browser
            await self._init_browser()
            
            # Get starting URLs
            start_urls = self.get_start_urls()
            
            for url in start_urls:
                try:
                    await self._scrape_page(url)
                except Exception as e:
                    self.log_error(f"Failed to scrape page {url}: {e}", url)
                    continue
            
            logger.info(f"Completed Playwright scraping. Found {len(self.scraped_data)} items")
            return self.scraped_data
            
        finally:
            await self._cleanup()
    
    async def _init_browser(self):
        """Initialize Playwright browser and context."""
        try:
            playwright = await async_playwright().start()
            
            # Launch browser
            if self.device_type == 'mobile':
                self.browser = await playwright.chromium.launch(
                    headless=self.headless,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                # Use mobile device context
                device = playwright.devices['iPhone 12']
                self.context = await self.browser.new_context(**device)
            else:
                self.browser = await playwright.chromium.launch(
                    headless=self.headless,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                self.context = await self.browser.new_context(
                    viewport=self.viewport,
                    user_agent=self.get_random_user_agent()
                )
            
            # Set up request interception if enabled
            if self.intercept_requests:
                await self.context.route("**/*", self._handle_route)
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set up additional page settings
            await self._setup_page()
            
            logger.info("Playwright browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Playwright browser: {e}")
            raise
    
    async def _setup_page(self):
        """Set up page with additional configurations."""
        # Set timeout
        self.page.set_default_timeout(self.wait_timeout)
        
        # Block unnecessary resources to speed up loading
        if self.block_resources:
            await self.page.route("**/*", lambda route: (
                route.abort() if route.request.resource_type in self.block_resources
                else route.continue_()
            ))
        
        # Set extra headers if configured
        extra_headers = self.source_config.get('extra_headers', {})
        if extra_headers:
            await self.page.set_extra_http_headers(extra_headers)
        
        # Handle JavaScript errors
        self.page.on('pageerror', lambda error: logger.warning(f"Page error: {error}"))
        
        # Handle console messages
        self.page.on('console', lambda msg: logger.debug(f"Console: {msg.text}"))
    
    async def _handle_route(self, route):
        """Handle network request interception."""
        request = route.request
        
        # Log requests if needed
        logger.debug(f"Request: {request.method} {request.url}")
        
        # Block certain resources
        if request.resource_type in self.block_resources:
            await route.abort()
        else:
            await route.continue_()
    
    def get_start_urls(self) -> List[str]:
        """Get list of starting URLs to scrape."""
        config = self.source_config.get('urls', {})
        start_urls = config.get('start_urls', [self.base_url])
        
        # Handle category-based URLs
        categories = config.get('categories', [])
        for category in categories:
            category_url = f"{self.base_url.rstrip('/')}/{category.get('path', '').lstrip('/')}"
            start_urls.append(category_url)
        
        return start_urls
    
    async def _scrape_page(self, url: str):
        """
        Scrape a single page using Playwright.
        
        Args:
            url: URL of the page to scrape
        """
        try:
            # Apply rate limiting
            self.rate_limiter.wait_if_needed()
            
            logger.debug(f"Navigating to: {url}")
            
            # Navigate to page
            response = await self.page.goto(url, wait_until='networkidle')
            
            if not response or response.status != 200:
                logger.warning(f"Failed to load {url}: Status {response.status if response else 'No response'}")
                return
            
            # Wait for specific content if configured
            await self._wait_for_content()
            
            # Handle any required interactions
            await self._handle_interactions()
            
            # Take screenshot if enabled
            if self.enable_screenshots:
                await self._take_screenshot(url)
            
            # Extract job data
            page_content = await self.page.content()
            job_data_list = self.extract_job_data(page_content, url)
            self.scraped_data.extend(job_data_list)
            
            # Update statistics
            self.stats['pages_scraped'] += 1
            self.stats['requests_made'] += 1
            self.stats['items_found'] += len(job_data_list)
            
            # Handle pagination
            await self._handle_pagination()
            
            logger.debug(f"Scraped {len(job_data_list)} jobs from {url}")
            
        except Exception as e:
            self.log_error(f"Error scraping page: {e}", url)
    
    async def _wait_for_content(self):
        """Wait for specific content to load."""
        wait_config = self.source_config.get('wait_for', {})
        
        # Wait for specific selector
        if self.wait_for_selector:
            try:
                await self.page.wait_for_selector(self.wait_for_selector, timeout=self.wait_timeout)
            except Exception as e:
                logger.warning(f"Wait for selector failed: {e}")
        
        # Wait for specific text
        wait_text = wait_config.get('text')
        if wait_text:
            try:
                await self.page.wait_for_function(
                    f"document.body.innerText.includes('{wait_text}')",
                    timeout=self.wait_timeout
                )
            except Exception as e:
                logger.warning(f"Wait for text failed: {e}")
        
        # Wait for network idle
        if wait_config.get('network_idle', True):
            await self.page.wait_for_load_state('networkidle')
        
        # Additional delay if configured
        delay = wait_config.get('delay', 0)
        if delay > 0:
            await asyncio.sleep(delay)
    
    async def _handle_interactions(self):
        """Handle required user interactions."""
        interactions = self.source_config.get('interactions', [])
        
        for interaction in interactions:
            try:
                action_type = interaction.get('type')
                selector = interaction.get('selector')
                
                if action_type == 'click' and selector:
                    await self.page.click(selector)
                    await asyncio.sleep(1)  # Wait after click
                
                elif action_type == 'fill' and selector:
                    value = interaction.get('value', '')
                    await self.page.fill(selector, value)
                
                elif action_type == 'select' and selector:
                    value = interaction.get('value', '')
                    await self.page.select_option(selector, value)
                
                elif action_type == 'scroll':
                    await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(2)
                
                elif action_type == 'wait':
                    duration = interaction.get('duration', 1)
                    await asyncio.sleep(duration)
                
            except Exception as e:
                logger.warning(f"Interaction failed: {e}")
    
    async def _take_screenshot(self, url: str):
        """Take screenshot for debugging."""
        try:
            # Create filename from URL
            filename = url.replace('https://', '').replace('http://', '').replace('/', '_')
            filename = f"screenshot_{filename}_{int(time.time())}.png"
            
            await self.page.screenshot(path=f"screenshots/{filename}", full_page=True)
            logger.debug(f"Screenshot saved: {filename}")
            
        except Exception as e:
            logger.warning(f"Screenshot failed: {e}")
    
    def extract_job_data(self, page_content: str, url: str) -> List[Dict[str, Any]]:
        """
        Extract job data from page content.
        
        This method uses the same logic as RequestsScraper but with
        Playwright-rendered content.
        
        Args:
            page_content: HTML content of the page
            url: URL of the page being scraped
            
        Returns:
            List of job data dictionaries
        """
        # Use the same extraction logic as RequestsScraper
        # but with Playwright-rendered content
        from bs4 import BeautifulSoup
        
        job_data_list = []
        
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            selectors = self.source_config.get('selectors', {})
            
            # Find job containers
            job_containers = self._find_job_containers(soup, selectors)
            
            for container in job_containers:
                try:
                    job_data = self._extract_single_job(container, selectors, url)
                    if job_data and self._validate_job_data(job_data):
                        job_data['scraper_type'] = 'playwright'
                        job_data_list.append(job_data)
                except Exception as e:
                    logger.warning(f"Failed to extract job data: {e}")
                    continue
            
        except Exception as e:
            self.log_error(f"HTML parsing failed: {e}", url)
        
        return job_data_list
    
    def _find_job_containers(self, soup: BeautifulSoup, selectors: Dict[str, Any]) -> List:
        """Find job containers in the HTML."""
        container_selector = selectors.get('job_container', '.job-item')
        
        if container_selector.startswith('//'):
            # XPath selector (convert to CSS selector if possible)
            containers = soup.find_all('div', class_='job-item')
        else:
            # CSS selector
            containers = soup.select(container_selector)
        
        return containers
    
    def _extract_single_job(self, container, selectors: Dict[str, Any], page_url: str) -> Dict[str, Any]:
        """Extract data for a single job from its container."""
        # Use similar logic as RequestsScraper
        # This is a simplified version - you can enhance based on specific needs
        job_data = {}
        
        # Extract basic fields using CSS selectors
        for field, selector in selectors.items():
            if field == 'job_container':
                continue
                
            try:
                if selector:
                    element = container.select_one(selector)
                    if element:
                        if field in ['application_link', 'notification_pdf', 'source_url']:
                            # Extract URL
                            href = element.get('href')
                            job_data[field] = self.resolve_url(href) if href else ""
                        else:
                            # Extract text
                            job_data[field] = self.clean_text(element.get_text())
            except Exception as e:
                logger.debug(f"Failed to extract {field}: {e}")
                job_data[field] = ""
        
        # Add metadata
        job_data['scraped_at'] = time.time()
        job_data['scraper_type'] = 'playwright'
        job_data['source_url'] = job_data.get('source_url') or page_url
        
        return job_data
    
    def _validate_job_data(self, job_data: Dict[str, Any]) -> bool:
        """Validate extracted job data."""
        required_fields = ['title']
        
        for field in required_fields:
            if not job_data.get(field):
                return False
        
        title = job_data.get('title', '')
        if len(title.strip()) < 5:
            return False
        
        return True
    
    async def _handle_pagination(self):
        """Handle pagination in Playwright."""
        try:
            pagination_config = self.source_config.get('pagination', {})
            if not pagination_config:
                return
            
            # Handle "Load More" buttons
            load_more_selector = pagination_config.get('load_more')
            if load_more_selector:
                try:
                    load_more_btn = await self.page.query_selector(load_more_selector)
                    if load_more_btn and await load_more_btn.is_visible():
                        await load_more_btn.click()
                        await self.page.wait_for_load_state('networkidle')
                        
                        # Extract additional content
                        page_content = await self.page.content()
                        job_data_list = self.extract_job_data(page_content, self.page.url)
                        self.scraped_data.extend(job_data_list)
                        
                except Exception as e:
                    logger.warning(f"Load more failed: {e}")
            
            # Handle next page navigation
            next_selector = pagination_config.get('next_page')
            if next_selector:
                try:
                    next_btn = await self.page.query_selector(next_selector)
                    if next_btn and await next_btn.is_visible():
                        await next_btn.click()
                        await self.page.wait_for_load_state('networkidle')
                        
                        # Recursively scrape next page
                        await self._scrape_page(self.page.url)
                        
                except Exception as e:
                    logger.warning(f"Next page navigation failed: {e}")
                    
        except Exception as e:
            logger.warning(f"Pagination handling failed: {e}")
    
    async def _cleanup(self):
        """Clean up browser resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            
            logger.debug("Playwright browser cleaned up")
            
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
    
    async def evaluate_javascript(self, script: str) -> Any:
        """
        Execute JavaScript in the browser context.
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Result of JavaScript execution
        """
        try:
            if self.page:
                return await self.page.evaluate(script)
        except Exception as e:
            logger.warning(f"JavaScript evaluation failed: {e}")
            return None
    
    async def get_network_requests(self) -> List[Dict[str, Any]]:
        """Get all network requests made during scraping."""
        # This would require setting up request logging
        # Implementation depends on specific requirements
        return []
