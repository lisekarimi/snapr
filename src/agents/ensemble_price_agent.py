"""Agent calling a remote ensemble model on Modal.

Computes final price from multiple predictions.
"""

import modal

from src.agents.base_agent import Agent
from src.agents.ft_price_agent import FTPriceAgent
from src.agents.rag_price_agent import RAGPriceAgent
from src.agents.xgb_price_agent import XGBoostPriceAgent
from src.config.constants import CURRENCY
from src.modal_services.app_config import APP_NAME


class EnsemblePriceAgent(Agent):
    """Agent that aggregates FT, RAG, and XGB predictions.

    Sends them to the remote EnsemblePricer on Modal.
    """

    name = "EnsemblePrice Agent"
    color = "magenta"

    def __init__(self) -> None:
        """Initialize the agent."""
        self._modal_called = False
        self.ft_agent = FTPriceAgent()
        self.rag_agent = RAGPriceAgent()
        self.xgb_agent = XGBoostPriceAgent()
        remote_ensemble = modal.Cls.from_name(APP_NAME, "EnsemblePricer")
        self.ensemble = remote_ensemble()
        self.log("is ready")

    def price(self, description: str) -> float:
        """Get individual predictions and pass them to the ensemble model."""
        ft_pred = self.ft_agent.price(description)
        rag_pred = self.rag_agent.price(description)
        xgb_pred = self.xgb_agent.price(description)

        if not self._modal_called:
            self.log("📡 Connecting to Modal — Loading trained linear model...")
            self._modal_called = True

        self.log(
            f"Predictions — FT={CURRENCY}{ft_pred}, "
            f"RAG={CURRENCY}{rag_pred}, "
            f"XGB={CURRENCY}{xgb_pred}"
        )

        try:
            result = self.ensemble.price.remote(ft_pred, rag_pred, xgb_pred)
            self.log(f"Final estimate: {CURRENCY}{result:.2f}")
            return result
        except Exception as e:
            self.log(f"[ERROR] Remote EnsemblePricer failed: {e}")
            raise RuntimeError("EnsemblePriceAgent failed to get final price.") from e
