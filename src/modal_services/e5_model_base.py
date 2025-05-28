"""Base class for E5 model handling.

Downloads, caches, and loads the model for reuse.
"""

import logging
import os

# Import CACHE_PATH from your config
from src.modal_services.app_config import CACHE_PATH

# Define the model directory using the imported CACHE_PATH
E5_MODEL_DIR = f"{CACHE_PATH}/e5_model"


class E5ModelBase:
    """Base class for downloading and loading the E5 model."""

    def setup_e5_model(self) -> None:
        """Downloads and loads the E5 embedding model."""
        try:
            # Lazy imports to avoid issues in Docker
            from huggingface_hub import snapshot_download
            from sentence_transformers import SentenceTransformer

            # Cache E5 embedding model into /cache/e5_model
            os.makedirs(E5_MODEL_DIR, exist_ok=True)
            if not os.listdir(E5_MODEL_DIR):
                snapshot_download("intfloat/e5-small-v2", local_dir=E5_MODEL_DIR)
                logging.info("E5 model downloaded.")

            self.vectorizer = SentenceTransformer(E5_MODEL_DIR, device="cuda")
            logging.info("E5 model loaded on GPU.")

        except Exception as e:
            logging.error(f"[E5ModelBase] Failed to setup E5 model: {e}")
            raise RuntimeError("[E5ModelBase] E5 model setup failed.") from e
