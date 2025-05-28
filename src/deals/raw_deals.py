"""Handles scraping and preprocessing logic before OpenAI interaction."""

import time
from typing import Dict, List, Self

import feedparser
import requests
from bs4 import BeautifulSoup

from src.config.constants import MAX_DEALS_PER_FEED
from src.config.feeds import CATEGORY_FEEDS
from src.utils.logger import console


def extract(html_snippet: str) -> str:
    """Cleans text from messy HTML with fallback handling."""
    soup = BeautifulSoup(html_snippet, "html.parser")
    snippet = soup.find("div", class_="snippet summary")

    # Extract inner HTML or fallback to full snippet
    raw_html = snippet.decode_contents() if snippet else html_snippet

    # Parse again to clean any nested/malformed HTML
    clean_soup = BeautifulSoup(raw_html, "html.parser")
    text = clean_soup.get_text(" ", strip=True)

    return text.replace("\n", " ")


class ScrapedDeal:
    """Represents a deal from an RSS feed.

    Flow: fetch() → __init__ → _load_content() → use methods.
    """

    category: str  # Deal type
    title: str  # Deal title
    summary: str  # RSS summary
    url: str  # Deal link
    details: str  # Full description
    features: str  # Feature list

    def __init__(self, entry: Dict[str, str]) -> None:
        """Initialize deal from RSS entry and fetch content."""
        # Basic metadata from RSS
        self.title = entry["title"]
        self.summary = extract(entry["summary"])
        self.url = entry["links"][0]["href"]

        # Initialize placeholders
        self.details = ""
        self.features = ""

        # Fetch and parse full deal content
        self._load_content()

    def _load_content(self) -> None:
        """Fetches and parses deal content; raises on failure to skip."""
        try:
            res = requests.get(self.url, timeout=5)
            res.raise_for_status()

            soup = BeautifulSoup(res.content, "html.parser")
            content = soup.find("div", class_="content-section")

            if content:
                text = content.get_text().replace("\nmore", "").replace("\n", " ")
                if "Features" in text:
                    self.details, self.features = text.split("Features", 1)
                else:
                    self.details = text
                    self.features = ""
            else:
                raise ValueError("No content section found.")

        except Exception as e:
            raise RuntimeError(f"Failed to load deal content from {self.url}: {e}")

    def __repr__(self) -> str:
        """Quick string representation of the deal."""
        return f"<{self.title}>"

    def describe(self) -> str:
        """Detailed description of the deal."""
        return (
            f"Title: {self.title.strip()}\n"
            f"Details: {self.details.strip()}\n"
            f"Features: {self.features.strip()}\n"
            f"URL: {self.url.strip()}"
        )

    @classmethod
    def fetch(cls, selected_categories: List[str]) -> List[Self]:
        """Parses RSS feeds into ScrapedDeal instances.

        Skips failed deals; stops app if all fail.
        """
        deals = []
        feed_urls = [
            CATEGORY_FEEDS[cat] for cat in selected_categories if cat in CATEGORY_FEEDS
        ]

        for feed_url in feed_urls:
            feed = cls._parse_feed(feed_url)
            if feed is None:
                continue

            console.print(
                f"[bold blue]DEBUG[/] {len(feed.entries)} entries found in feed: "
                f"{feed_url}"
            )

            for entry in feed.entries[:MAX_DEALS_PER_FEED]:
                cls._process_deal(entry, deals)

            # Throttle requests to avoid hitting servers too fast
            time.sleep(0.5)

        if not deals:
            raise RuntimeError("❌ All deals failed to load. Stopping.")

        return deals

    @staticmethod
    def _parse_feed(feed_url: str) -> feedparser.FeedParserDict | None:
        """Helper method to parse the RSS feed and return the feed data."""
        feed = feedparser.parse(feed_url)
        if feed.bozo:
            console.print(
                f"[bold red]ERROR[/] Failed to parse RSS feed: {feed_url} "
                f"({feed.bozo_exception})"
            )
            return None
        return feed

    @staticmethod
    def _process_deal(entry: Dict[str, str], deals: List[Self]) -> None:
        """Helper method to process each RSS entry and add valid deals."""
        try:
            deal = ScrapedDeal(entry)
            deals.append(deal)
        except Exception as e:
            console.print(
                f"[bold yellow]WARN[/] Skipped deal "
                f"'{entry.get('title', 'Unknown')}' due to error: {e}"
            )
