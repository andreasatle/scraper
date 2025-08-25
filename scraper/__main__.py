import asyncio
import argparse
import json
from typing import List, Dict, Any

from .scraping_config import ScrapingConfig
from .web_scraper import WebScraper


class ScraperCLI:
    """Command-line interface for the scraper"""
    
    @staticmethod
    def build_arg_parser() -> argparse.ArgumentParser:
        """Build the command line argument parser"""
        parser = argparse.ArgumentParser(
            description="Playwright scraper with optional JS automation (scroll/click/eval)"
        )
        parser.add_argument("url", help="Start URL")
        parser.add_argument("--depth", type=int, default=0, help="Crawl depth (0 = single page)")
        parser.add_argument("--max-pages", type=int, default=50, help="Max pages (safety cap)")
        parser.add_argument("--delay-ms", type=int, default=500, help="Delay between page visits")
        parser.add_argument("--concurrency", type=int, default=5, help="Concurrent pages")
        parser.add_argument("--concurrent-batch", type=int, default=10, 
                          help="Batch size before expanding frontier")
        parser.add_argument("--headful", action="store_true", help="Show the browser window")

        # Navigation timeouts & UA/viewport
        parser.add_argument("--goto-timeout-ms", type=int, default=30000)
        parser.add_argument("--wait-timeout-ms", type=int, default=15000)
        parser.add_argument("--post-click-wait-ms", type=int, default=2000)
        parser.add_argument("--user-agent", default=None)
        parser.add_argument("--vw", type=int, default=1366)
        parser.add_argument("--vh", type=int, default=900)

        # JS automation knobs
        parser.add_argument("--wait-selector", default=None, 
                          help="Wait for this selector before JS automation/extraction")
        parser.add_argument("--click-selector", action="append", 
                          help="Click CSS selector(s) before extraction; repeatable")
        parser.add_argument("--scrolls", type=int, default=0, help="Scroll this many times")
        parser.add_argument("--scroll-wait-ms", type=int, default=1000, help="Wait between scrolls")
        parser.add_argument("--scroll-until-end", action="store_true", 
                          help="Keep scrolling until page height is stable")
        parser.add_argument("--eval-js", default=None, help="Custom JS (inline) to run on each page")
        parser.add_argument("--eval-js-file", default=None, 
                          help="Path to a JS file to run on each page")

        # Extraction toggles
        parser.add_argument("--tables", action="store_true", help="Include table extraction")
        
        return parser

    @staticmethod
    def parse_args_to_config(args: argparse.Namespace) -> ScrapingConfig:
        """Convert parsed arguments to ScrapingConfig"""
        return ScrapingConfig(
            depth=args.depth,
            max_pages=args.max_pages,
            delay_ms=args.delay_ms,
            concurrency=args.concurrency,
            concurrent_batch=args.concurrent_batch,
            headful=args.headful,
            goto_timeout_ms=args.goto_timeout_ms,
            wait_timeout_ms=args.wait_timeout_ms,
            post_click_wait_ms=args.post_click_wait_ms,
            user_agent=args.user_agent,
            vw=args.vw,
            vh=args.vh,
            wait_selector=args.wait_selector,
            click_selectors=args.click_selector or [],
            scrolls=args.scrolls,
            scroll_wait_ms=args.scroll_wait_ms,
            scroll_until_end=args.scroll_until_end,
            eval_js=args.eval_js,
            eval_js_file=args.eval_js_file,
            include_tables=args.tables,
        )


# Convenience functions for backward compatibility
async def scrape_one_page_async(url: str, depth: int = 0) -> List[Dict[str, Any]]:
    """Async function to scrape a single page"""
    config = ScrapingConfig(depth=depth, scroll_until_end=True)
    scraper = WebScraper(config)
    return await scraper.scrape(url)


def scrape_one_page(url: str, depth: int = 0) -> List[Dict[str, Any]]:
    """Sync function to scrape a single page"""
    return asyncio.run(scrape_one_page_async(url, depth))


def main() -> None:
    parser = ScraperCLI.build_arg_parser()
    args = parser.parse_args()

    config = ScraperCLI.parse_args_to_config(args)
    scraper = WebScraper(config)

    results = asyncio.run(scraper.scrape(args.url))

    for result in results:
        print(f"{json.dumps(result, ensure_ascii=False)}\n\n")


if __name__ == "__main__":
    main()
