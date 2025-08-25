from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from typing import Final


@dataclass
class JsScript:
    name: str
    content: str


class JsManager:
    """Loads and formats bundled JS scripts for Playwright page.evaluate usage."""

    _SCROLL_FILE: Final[str] = "js/scroll.js"
    _EXTRACT_TEXT_FILE: Final[str] = "js/extract_text.js"
    _EXTRACT_LINKS_FILE: Final[str] = "js/extract_links.js"
    _EXTRACT_TABLES_FILE: Final[str] = "js/extract_tables.js"

    def __init__(self, package: str = __package__ or "scraper") -> None:
        self.package = package
        self._cache: dict[str, JsScript] = {}

    def _read_text(self, relative_path: str) -> str:
        # resources.files available in Python 3.9+ with importlib.resources
        file_ref = resources.files(self.package).joinpath(relative_path)
        return file_ref.read_text(encoding="utf-8")

    def _get_cached(self, name: str, path: str) -> JsScript:
        if name in self._cache:
            return self._cache[name]
        content = self._read_text(path)
        script = JsScript(name=name, content=content)
        self._cache[name] = script
        return script

    def scroll(self, tries: int, wait_ms: int, until_end: bool) -> str:
        tpl = self._get_cached("scroll", self._SCROLL_FILE).content
        tpl = tpl.replace("__TRIES__", str(tries if tries > 0 else 999999))
        tpl = tpl.replace("__WAIT_MS__", str(wait_ms))
        tpl = tpl.replace("__UNTIL_END__", "true" if until_end else "false")
        return tpl

    def extract_text(self) -> str:
        return self._get_cached("extract_text", self._EXTRACT_TEXT_FILE).content

    def extract_links(self) -> str:
        return self._get_cached("extract_links", self._EXTRACT_LINKS_FILE).content

    def extract_tables(self) -> str:
        return self._get_cached("extract_tables", self._EXTRACT_TABLES_FILE).content
