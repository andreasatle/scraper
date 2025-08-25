import json
import pathlib
import sys
from playwright.async_api import Page
from .scraping_config import ScrapingConfig


class PageAutomator:
    """Handles page automation tasks like scrolling, clicking, and JavaScript execution"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config

    async def run_page_automation(self, page: Page) -> None:
        """Run all configured page automation tasks"""
        # Wait for selector if specified
        if self.config.wait_selector:
            try:
                await page.wait_for_selector(
                    self.config.wait_selector, 
                    timeout=self.config.wait_timeout_ms
                )
            except Exception:
                pass

        # Auto scroll
        if self.config.scrolls or self.config.scroll_until_end:
            await self._scroll_page(page)

        # Click selectors
        for selector in self.config.click_selectors:
            await self._click_selector(page, selector)

        # Run custom JavaScript
        await self._run_custom_js(page)

    async def _scroll_page(self, page: Page) -> None:
        """Scroll the page according to configuration"""
        await page.evaluate(
            f"""async () => {{
                const sleep = ms => new Promise(r => setTimeout(r, ms));
                let prev = 0;
                let stableCount = 0;
                const maxStable = 3;
                const tries = {self.config.scrolls if self.config.scrolls else 999999};
                
                for (let i = 0; i < tries; i++) {{
                    window.scrollTo(0, document.body.scrollHeight);
                    await sleep({self.config.scroll_wait_ms});
                    const h = document.body.scrollHeight;
                    
                    if ({'true' if self.config.scroll_until_end else 'false'}) {{
                        if (h === prev) {{
                            stableCount++;
                            if (stableCount >= maxStable) break;
                        }} else {{
                            stableCount = 0;
                        }}
                        prev = h;
                    }}
                }}
            }}"""
        )

    async def _click_selector(self, page: Page, selector: str) -> None:
        """Click a specific selector on the page"""
        try:
            button = await page.query_selector(selector)
            if button:
                await button.click()
                await page.wait_for_load_state(
                    "networkidle", 
                    timeout=self.config.post_click_wait_ms
                )
        except Exception:
            try:
                await page.wait_for_timeout(self.config.post_click_wait_ms)
            except Exception:
                pass

    async def _run_custom_js(self, page: Page) -> None:
        """Run custom JavaScript code on the page"""
        js_code = None
        if self.config.eval_js:
            js_code = self.config.eval_js
        elif self.config.eval_js_file:
            js_code = pathlib.Path(self.config.eval_js_file).read_text(encoding="utf-8")
        
        if js_code:
            wrapped = f"(async () => {{ {js_code} }})()"
            try:
                await page.evaluate(wrapped)
            except Exception as e:
                print(json.dumps({"_warning": f"eval_js failed: {e}"}), file=sys.stderr)
