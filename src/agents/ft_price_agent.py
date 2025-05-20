"""FTPriceAgent uses a remote fine-tuned LLM on Modal.

Predicts item prices from descriptions.
"""

import modal

from src.agents.base_agent import Agent
from src.modal_services.app_config import APP_NAME


class FTPriceAgent(Agent):
    """Agent for running a fine-tuned LLM remotely."""

    name = "FTPrice Agent"
    color = "red"

    def __init__(self) -> None:
        """Initialize agent with Modal class instance."""
        self._modal_called = False
        ft_pricer = modal.Cls.from_name(APP_NAME, "FTPricer")
        self.ftpricer = ft_pricer()
        self.log("is ready")

    def price(self, description: str) -> float:
        """Remote call to estimate price, with error handling."""
        if not self._modal_called:
            self.log("🧠 Calling Modal's fine-tuned LLM...")
            self._modal_called = True
        try:
            result = self.ftpricer.price.remote(
                description
            )  # 2nd API call: run price method
            # self.log(f"predicting ${result:.2f} ✅")
            return result
        except Exception as e:
            self.log(f"[ERROR] Remote pricing failed: {e}")
            raise RuntimeError("FTPriceAgent failed to get price from Modal.") from e
