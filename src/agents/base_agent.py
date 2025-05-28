"""Base class for Agents, providing colorful logging with Rich."""

from src.config.logging_queue import log_queue
from src.utils.logger import console


class Agent:
    """Abstract superclass for Agents, with colorful Rich logging."""

    name: str = ""
    color: str = "white"

    def log(self, message: str) -> None:
        """Print log with colored message using Rich."""
        # Terminal (Rich)
        console.print(f"[{self.color} on black][{self.name}] {message}[/]")

        # Gradio UI (HTML)
        log_queue.put(
            f"<span style='color:{self.color}'>[{self.name}] {message}</span><br>"
        )
