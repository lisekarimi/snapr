"""PlanningAgent coordinates deal scanning and enrichment."""

import json
from typing import List

from rich import print_json

from src.agents.base_agent import Agent
from src.agents.deal_scanner_agent import DealScannerAgent
from src.agents.ensemble_price_agent import EnsemblePriceAgent
from src.config.constants import CURRENCY, DEAL_THRESHOLD
from src.deals.structured_deals import OpportunitiesCollection, Opportunity
from src.utils.logger import console
from src.utils.memory_utils import save_opportunities_to_memory


class PlanningAgent(Agent):
    """Create instances of the Agents that this planner coordinates across."""

    name = "Planning Agent"
    color = "cyan"

    def __init__(self) -> None:
        """Initialize agents."""
        self.log("🧠 Let’s wake up the agents — time to sniff out some sweet deals!")
        self.log("is ready")
        self.scanner = DealScannerAgent()
        self.ensemble = EnsemblePriceAgent()
        self.log("🚀 All AI Agents are caffeinated, calibrated, and ready to hustle..")

    def scan_deals(self, categories: List[str]) -> List[Opportunity]:
        """Scans deals and returns GPT-processed opportunities."""
        result = self.scanner.scan(categories)
        if result is None:
            self.log("❌ No valid deals found.")
            return []
        return result.opportunities

    def enrich(self, opportunity: Opportunity) -> Opportunity:
        """Add estimated market price and discount to an opportunity."""
        estimate = self.ensemble.price(opportunity.product_description)
        discount = round(estimate - opportunity.price, 2)
        opportunity.estimate = estimate
        opportunity.discount = discount
        return opportunity

    def _log_result(self, idx: int, opportunity: Opportunity) -> None:
        """Logs if a deal was accepted or rejected.

        Decision is based on discount vs. threshold.

        """
        if opportunity.discount >= DEAL_THRESHOLD:
            self.log(
                f"✅ Deal #{idx} accepted — discount: "
                f"{CURRENCY}{opportunity.discount:.2f}"
            )
        else:
            self.log(
                f"❌ Deal #{idx} rejected — discount below threshold: "
                f"{CURRENCY}{opportunity.discount:.2f}"
            )

    def _report_summary(self, enriched: List[Opportunity]) -> None:
        """Display a summary of accepted opportunities after enrichment."""
        if not enriched:
            self.log("❌ No opportunities met the discount threshold.")
        else:
            for opp in enriched:
                console.print(
                    f"- {opp.product_description}\n"
                    f"  Price: {CURRENCY}{opp.price:.2f} | "
                    f"AI Estimate: {CURRENCY}{opp.estimate:.2f} | "
                    f"Discount: {CURRENCY}{opp.discount:.2f}\n"
                    f"  URL: {opp.url}\n"
                )

    def plan(self, categories: List[str]) -> List[Opportunity]:
        """Full pipeline: scan → enrich → filter → save."""
        self.log(
            "************** SCANNING INITIATED — HUNTING JUICY DEALS...**************"
        )

        deals = self.scan_deals(categories)
        if not deals:
            self.log("❌ No deals found from scanner.")
            return []
        print_json(
            data=json.loads(
                OpportunitiesCollection(opportunities=deals).model_dump_json()
            )
        )  # For debugging/inspection

        self.log(
            "************** SCANNING COMPLETE — STARTING ENRICHMENT **************"
        )

        enriched = []
        for idx, deal in enumerate(deals, start=1):
            opportunity = self.enrich(deal)
            self._log_result(idx, opportunity)
            if opportunity.discount >= DEAL_THRESHOLD:
                enriched.append(opportunity)

        self.log(
            "************** ENRICHMENT COMPLETE — SAVING OPPORTUNITIES **************"
        )
        save_opportunities_to_memory([opp.model_dump() for opp in enriched])
        self.log(f"💾 {len(enriched)} top deals saved to memory.")

        self._report_summary(enriched)
        self.log(
            "************** ✅ MISSION COMPLETE — BEST DEALS LOCKED IN **************"
        )

        return enriched
