# Scraper

Playwright-based web scraper with a class-based architecture.

## Install

- Ensure Python 3.12+
- Install dependencies and package (editable recommended):

```bash
pip install -e .
python -m playwright install chromium
```

## Usage

### CLI

```bash
python -m scraper https://example.com --depth 1 --max-pages 20
# after install
scraper https://example.com --depth 1 --max-pages 20
```

Common flags:
- `--depth`: crawl depth (0 = only the start URL)
- `--max-pages`: safety cap for total pages visited
- `--delay-ms`: delay between page visits
- `--concurrency`: concurrent pages
- `--concurrent-batch`: drain batch before expanding frontier
- `--headful`: open browser window
- `--goto-timeout-ms`, `--wait-timeout-ms`, `--post-click-wait-ms`
- `--user-agent`, `--vw`, `--vh`
- `--wait-selector`: wait for this selector before automation/extraction
- `--click-selector`: repeatable; click elements before extraction
- `--scrolls`, `--scroll-wait-ms`, `--scroll-until-end`
- `--eval-js`, `--eval-js-file`: optional custom JS per page

### Python API

```python
import asyncio
from scraper import WebScraper, ScrapingConfig

config = ScrapingConfig(depth=1, max_pages=10, scroll_until_end=True)
results = asyncio.run(WebScraper(config).scrape("https://example.com"))

for r in results:
    print(r["url"], len(r["text"]))
```

## Output

Each result is a JSON object with:
- `url`: page URL
- `text`: visible structured text
- `links`: list of `{href, text}` (normalized, deduped)
- `depth`: crawl depth for that page
- `error`: present if navigation/extraction failed

## How it works

- `WebScraper`: orchestrates crawling
- `PageAutomator`: waits, clicks, scrolling (uses bundled JS)
- `ContentExtractor`: extracts visible text and links (uses bundled JS)
- `URLNormalizer`: URL normalization and domain policy
- `JsManager`: loads JS from `scraper/js` and parameterizes snippets

## Notes

- Only same-domain links are enqueued. Assets/binaries are skipped.
- Depth applies to frontier expansion: links from depth `d` are added only if `d < depth`.
- Large pages: enable `--scroll-until-end` or set `--scrolls`.

## Troubleshooting

- No additional pages at `--depth 1`:
  - Target has few/hidden internal links, or all were filtered/duplicates.
  - Try a different URL, increase `--max-pages`, or set `--concurrent-batch 1`.
- Timeouts: increase `--goto-timeout-ms`/`--wait-timeout-ms`.
- Headed mode for debugging: add `--headful`.

## Development

Run lints/tests locally as needed. To modify bundled JS, edit files in `scraper/js/`.
