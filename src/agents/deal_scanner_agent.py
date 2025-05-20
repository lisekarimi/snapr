"""Scan deals and return top 5 via OpenAI.

1. Fetch deals from RSS feeds.
2. Prompt OpenAI with the deal list.
3. Return top 5 detailed, clearly priced deals as structured JSON.
"""

import json
import os
from typing import Any, Dict, List, Optional

from src.agents.base_agent import Agent
from src.config.constants import DEALS_FILE
from src.deals.raw_deals import ScrapedDeal
from src.deals.structured_deals import OpportunitiesCollection
from src.models.frontier_model import OPENAI_MODEL, openai


class DealScannerAgent(Agent):
    """Agent for scanning and filtering deals.

    Processes them via OpenAI.
    """

    name = "Deal Scanner Agent"
    color = "green"

    SYSTEM_PROMPT = """
    You are a deal filtering assistant.

    Your task is to identify the 5 deals with the most detailed product descriptions 
    and clearly stated prices. Focus only on the product itself — not the deal terms, 
    discounts, or promotions.

    Only include deals where the price is explicitly mentioned and easy to extract. 
    Avoid entries with phrases like "$XXX off" or "reduced by $XXX" — those are not 
    valid prices. Only include deals when you are confident about the actual 
    product price.

    Respond strictly in JSON with no explanation, using the following format:

    {
    "deals": [
        {
        "product_description": "A clear, 4–5 sentence summary of the product.",
        "price": 99.99,
        "url": "..."
        },
        ...
    ]
    }"""

    def __init__(self, memory_path: str = DEALS_FILE) -> None:
        """Initialize OpenAI client."""
        self.openai = openai
        self.memory_path = memory_path
        self.log("is ready")

    def _load_memory(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load memory from file, returning seen URLs and the full memory."""
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, "r") as f:
                    memory_json = json.load(f)
                seen_urls = [op["url"] for op in memory_json.get("opportunities", [])]
                return {
                    "seen_urls": seen_urls,
                    "memory": memory_json.get("opportunities", []),
                }
            except (json.JSONDecodeError, KeyError, IOError) as e:
                self.log(f"Error loading memory: {e}. Creating new memory.")
                return {"seen_urls": [], "memory": []}
        else:
            self.log("No memory file found. Assuming first run")
            return {"seen_urls": [], "memory": []}

    def fetch_deals(self, categories: List[str]) -> List[ScrapedDeal]:
        """Fetch new RSS deals not present in memory."""
        self.log("is fetching deals from RSS feed")

        # Load memory to get seen URLs
        memory_data = self._load_memory()
        seen_urls = set(memory_data["seen_urls"])

        # Fetch all deals and filter out seen ones
        try:
            scraped = ScrapedDeal.fetch(categories)
            result = [deal for deal in scraped if deal.url not in seen_urls]
            overlap = [deal for deal in scraped if deal.url in seen_urls]
            self.log(f"{len(overlap)} deals skipped")
            self.log(f"{len(result)} new deals fetched")
            return result
        except Exception as e:
            self.log(f"Error fetching deals: {e}")
            return []

    def make_user_prompt(self, scraped: List[ScrapedDeal]) -> str:
        """Build the full user prompt for OpenAI."""
        return (
            "Select the 5 best deals with the clearest product descriptions "
            "and exact prices. Here is the list:\n\n"
            + "\n\n".join(deal.describe() for deal in scraped)
        )

    def scan(self, categories: List[str]) -> Optional[OpportunitiesCollection]:
        """Return top 5 new deals."""
        # Step 1: Fetch new deals not already in memory
        scraped = self.fetch_deals(categories)
        if not scraped:
            self.log("❌ found no new deals to process ")
            return None

        # Step 2: Construct prompt with all new deals
        user_prompt = self.make_user_prompt(scraped)

        # Step 3: Call OpenAI - allow RuntimeError to propagate
        result = self._call_openai(user_prompt)

        # Step 4: Filter out invalid deals
        filtered_result = self._filter_invalid_deals(result)

        return filtered_result if filtered_result.opportunities else None

    def _call_openai(self, user_prompt: str) -> OpportunitiesCollection:
        """Call OpenAI API to get the processed deals."""
        self.log("📞 is calling OpenAI")
        try:
            result = self.openai.beta.chat.completions.parse(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=OpportunitiesCollection,
            )
        except Exception as e:
            self.log(f"[ERROR] OpenAI call failed: {e}")
            raise RuntimeError(
                "DealScannerAgent failed to get response from OpenAI."
            ) from e
        return result

    def _filter_invalid_deals(
        self, result: OpportunitiesCollection
    ) -> OpportunitiesCollection:
        """Filter out deals with invalid prices."""
        result = result.choices[0].message.parsed
        result.opportunities = [op for op in result.opportunities if op.price > 0]
        self.log(f"✅ received {len(result.opportunities)} valid opportunities ")
        return result
