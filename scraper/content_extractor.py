from typing import List, Dict, Tuple, Optional
from playwright.async_api import Page
from .url_normalizer import URLNormalizer
from .js_manager import JsManager


class ContentExtractor:
    """Handles content extraction from web pages"""

    def __init__(self, js_manager: Optional[JsManager] = None) -> None:
        self.js_manager = js_manager or JsManager()
    
    async def extract_content(self, page: Page) -> Tuple[str, List[Dict[str, str]]]:
        """Extract text content and links from a page"""
        # Wait for initial states
        try:
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

        # Extract visible text
        text = await self._extract_text(page)
        
        # Extract and clean links
        links = await self._extract_links(page)
        cleaned_links = self._clean_links(links, page.url)
        
        return text, cleaned_links

    async def _extract_text(self, page: Page) -> str:
        """Extract visible text content from the page"""
        script = self.js_manager.extract_text()
        return await page.evaluate(script)

    async def _extract_links(self, page: Page) -> List[Dict[str, str]]:
        """Extract visible links from the page"""
        script = self.js_manager.extract_links()
        return await page.evaluate(script)

    @staticmethod
    def _clean_links(links: List[Dict[str, str]], base_url: str) -> List[Dict[str, str]]:
        """Clean and normalize extracted links"""
        cleaned = []
        for link in links:
            href = (link.get("href") or "").strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            abs_url = URLNormalizer.absolutize(base_url, href)
            cleaned.append({"text": link.get("text", ""), "href": abs_url})

        # De-dupe by href
        dedup = {}
        for item in cleaned:
            href_n = URLNormalizer.normalize_url(item["href"])
            # keep the first non-empty text if available
            if href_n not in dedup or (not dedup[href_n] and item["text"]):
                dedup[href_n] = item["text"]
        
        return [{"href": k, "text": v} for k, v in dedup.items()]
