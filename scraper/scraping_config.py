from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ScrapingConfig:
    """Configuration class for scraping parameters"""
    depth: int = 0
    max_pages: int = 50
    delay_ms: int = 500
    concurrency: int = 5
    concurrent_batch: int = 10
    headful: bool = False
    goto_timeout_ms: int = 30000
    wait_timeout_ms: int = 15000
    post_click_wait_ms: int = 2000
    user_agent: Optional[str] = None
    vw: int = 1366
    vh: int = 900
    wait_selector: Optional[str] = None
    click_selectors: List[str] = None
    scrolls: int = 0
    scroll_wait_ms: int = 1000
    scroll_until_end: bool = False
    eval_js: Optional[str] = None
    eval_js_file: Optional[str] = None

    def __post_init__(self):
        if self.click_selectors is None:
            self.click_selectors = []
