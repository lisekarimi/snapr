"""Handles the integration of RAG model with Modal to predict item prices."""

import modal

from src.agents.base_agent import Agent
from src.modal_services.app_config import APP_NAME


class RAGPriceAgent(Agent):
    """RAGPriceAgent connects to a remote Modal container.

    Uses a RAG pipeline to predict item prices.
    """

    name = "RAGPrice Agent"
    color = "blue"

    def __init__(self) -> None:
        """Initialize the agent."""
        self._modal_called = False
        remote_rag_pricer = modal.Cls.from_name(APP_NAME, "RAGPricer")
        self.rag = remote_rag_pricer()
        self.log("is ready")

    def price(self, description: str) -> float:
        """Call the remote RAGPricer to estimate price."""
        if not self._modal_called:
            self.log("📡 Connecting to Modal — loading embedding model and ChromaDB...")
            self._modal_called = True
        try:
            result = self.rag.price.remote(description)
            # self.log(f"predicting ${result:.2f} ✅")
            return result
        except Exception as e:
            self.log(f"[ERROR] Remote RAGPricer failed: {e}")
            raise RuntimeError("RAGPriceAgent failed to get price from Modal.") from e
