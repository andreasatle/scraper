from collections import deque
from typing import List, Dict, Set, Any
import asyncio
import re
from playwright.async_api import async_playwright, BrowserContext
from .url_normalizer import URLNormalizer
from .page_automator import PageAutomator
from .content_extractor import ContentExtractor
from .scraping_config import ScrapingConfig
from .js_manager import JsManager


class WebScraper:
    """Main scraper class that orchestrates the crawling process"""
    
    def __init__(self, config: ScrapingConfig, js_manager: JsManager | None = None):
        self.config = config
        self.js_manager = js_manager or JsManager()
        self.url_normalizer = URLNormalizer()
        self.page_automator = PageAutomator(config, js_manager=self.js_manager)
        self.content_extractor = ContentExtractor(js_manager=self.js_manager)
        self.seen_urls: Set[str] = set()
        self.results: List[Dict[str, Any]] = []

    async def scrape(self, start_url: str) -> List[Dict[str, Any]]:
        """Main scraping method"""
        # Normalize the start URL before seeding the queue
        start_url = self.url_normalizer.normalize_url(start_url)
        queue = deque([(start_url, 0)])
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=not self.config.headful)
            context = await browser.new_context(
                user_agent=self.config.user_agent or "Mozilla/5.0 (compatible; PlaywrightScraper/2.0)",
                viewport={"width": self.config.vw, "height": self.config.vh}
            )
            
            semaphore = asyncio.Semaphore(self.config.concurrency)
            
            try:
                await self._process_queue(queue, context, semaphore, start_url)
            finally:
                await context.close()
                await browser.close()
        
        return self.results

    async def _process_queue(self, queue: deque, context: BrowserContext, 
                           semaphore: asyncio.Semaphore, start_url: str) -> None:
        """Process the URL queue"""
        tasks = []
        
        while queue and len(self.seen_urls) < self.config.max_pages:
            url, depth = queue.popleft()
            url = self.url_normalizer.normalize_url(url)
            
            if url in self.seen_urls:
                continue
                
            self.seen_urls.add(url)
            tasks.append(asyncio.create_task(
                self._visit_url(url, depth, context, semaphore)
            ))

            # Drain a batch, then expand from each result's own depth
            if not queue or len(tasks) >= self.config.concurrent_batch:
                done = await asyncio.gather(*tasks)
                tasks.clear()

                for result in done:
                    result_depth = result.get("depth", 0)
                    if result_depth < self.config.depth:
                        await self._expand_frontier(result, queue, start_url, result_depth)

    async def _visit_url(self, url: str, depth: int, context: BrowserContext, 
                        semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """Visit a single URL and extract content"""
        async with semaphore:
            page = await context.new_page()
            try:
                await page.goto(url, timeout=self.config.goto_timeout_ms, 
                               wait_until="domcontentloaded")
                await self.page_automator.run_page_automation(page)
                text, links = await self.content_extractor.extract_content(page)
                
                result = {
                    "url": url, 
                    "text": text, 
                    "links": links, 
                    "depth": depth
                }
                self.results.append(result)
                
                await asyncio.sleep(self.config.delay_ms / 1000)
                return result
                
            except Exception as e:
                result = {
                    "url": url, 
                    "error": str(e), 
                    "text": "", 
                    "links": [], 
                    "depth": depth
                }
                self.results.append(result)
                return result
            finally:
                await page.close()

    async def _expand_frontier(self, result: Dict[str, Any], queue: deque, 
                              start_url: str, current_depth: int) -> None:
        """Expand the crawling frontier with new URLs"""
        for link in result.get("links", []):
            href = self.url_normalizer.normalize_url(link["href"])
            
            if (self.url_normalizer.same_domain(start_url, href) and
                href not in self.seen_urls and
                len(self.seen_urls) + len(queue) < self.config.max_pages):
                
                # Skip typical binary files
                if re.search(r"\.(pdf|zip|jpg|jpeg|png|gif|webp|mp4|mov|avi|mp3)(\?.*)?$", 
                            href, re.I):
                    continue
                    
                queue.append((href, current_depth + 1))
