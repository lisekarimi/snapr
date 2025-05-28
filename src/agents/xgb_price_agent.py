"""Handles the integration of XGBoost model with Modal to predict item prices."""

import modal

from src.agents.base_agent import Agent
from src.modal_services.app_config import APP_NAME


class XGBoostPriceAgent(Agent):
    """XGBoostPriceAgent connects to a remote Modal container.

    Uses E5 and XGBoost to predict prices from descriptions.
    """

    name = "XGBPrice Agent"
    color = "yellow"

    def __init__(self) -> None:
        """Initialize the agent."""
        self._modal_called = False
        remote_xgb_pricer = modal.Cls.from_name(APP_NAME, "XGBPricer")
        self.xgb = remote_xgb_pricer()
        self.log("is ready")

    def price(self, description: str) -> float:
        """Call the remote XGBPricer to estimate price."""
        if not self._modal_called:
            self.log("📡 Connecting to Modal — loading XGBoost and embedding model...")
            self._modal_called = True
        try:
            result = self.xgb.price.remote(description)
            # self.log(f"predicting ${result:.2f} ✅")
            return result
        except Exception as e:
            self.log(f"[ERROR] Remote XGBPricer failed: {e}")
            raise RuntimeError(
                "XGBoostPriceAgent failed to get price from Modal."
            ) from e
