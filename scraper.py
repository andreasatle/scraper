# scraper.py
import asyncio
import re
import sys
import argparse
import json
import pathlib
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from scraping_config import ScrapingConfig
from url_normalizer import URLNormalizer
from page_automator import PageAutomator
from content_extractor import ContentExtractor
from web_scraper import WebScraper
from scraper.__main__ import main



if __name__ == "__main__":
    main()
