from typing import List, Dict, Tuple
from playwright.async_api import Page
from .url_normalizer import URLNormalizer


class ContentExtractor:
    """Handles content extraction from web pages"""
    
    @staticmethod
    async def extract_content(page: Page) -> Tuple[str, List[Dict[str, str]]]:
        """Extract text content and links from a page"""
        # Wait for initial states
        try:
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

        # Extract visible text
        text = await ContentExtractor._extract_text(page)
        
        # Extract and clean links
        links = await ContentExtractor._extract_links(page)
        cleaned_links = ContentExtractor._clean_links(links, page.url)
        
        return text, cleaned_links

    @staticmethod
    async def _extract_text(page: Page) -> str:
        """Extract visible text content from the page"""
        return await page.evaluate("""
() => {
  function visible(el) {
    const cs = getComputedStyle(el);
    if (!cs || cs.visibility === "hidden" || cs.display === "none") return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
  
  const sels = ["main","article","section","h1","h2","h3","h4","h5","h6","p"];
  const nodes = Array.from(document.querySelectorAll(sels.join(",")))
    .filter(visible)
    .map(n => n.innerText.trim())
    .filter(Boolean);

  const out = [];
  const seen = new Set();
  for (const line of nodes) {
    const norm = line.replace(/\\s+/g, " ").slice(0, 200);
    if (!seen.has(norm)) { 
      seen.add(norm); 
      out.push(line); 
    }
  }
  return out.join("\\n");
}
        """)

    @staticmethod
    async def _extract_links(page: Page) -> List[Dict[str, str]]:
        """Extract visible links from the page"""
        return await page.evaluate("""
() => {
  function visible(el) {
    const cs = getComputedStyle(el);
    if (!cs || cs.visibility === "hidden" || cs.display === "none") return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }
  
  return Array.from(document.querySelectorAll("a[href]"))
    .filter(visible)
    .map(a => ({ 
      text: a.innerText.trim().replace(/\\s+/g," "), 
      href: a.getAttribute("href") 
    }));
}
        """)

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
