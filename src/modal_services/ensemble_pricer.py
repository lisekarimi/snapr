"""Remote Modal service for price prediction.

Combines outputs from multiple agents using an ensemble model.
"""

# Standard library imports
import logging

import modal

# Third-party imports
# Local imports
from src.modal_services.app_config import (
    CACHE_PATH,
    app,
    modal_class_kwargs,
)

# Configure logging after all imports
logging.basicConfig(level=logging.INFO)

REPO_ID = "lisekarimi/smart-deal-finder-models"

# Local paths inside Modal volume
ENSEMBLE_MODEL_DIR = f"{CACHE_PATH}/ensemble_model"
ENSEMBLE_MODEL_FILENAME = "ensemble_model.pkl"


@app.cls(**modal_class_kwargs)
class EnsemblePricer:
    """Modal class for ensemble price prediction from agent outputs."""

    @modal.enter()
    def setup(self) -> None:
        """Loads ensemble model from Hugging Face into Modal cache."""
        try:
            # Lazy load hf_hub_download and joblib
            import joblib
            from huggingface_hub import hf_hub_download

            logging.info("Downloading Ensemble model...")
            model_path = hf_hub_download(
                repo_id=REPO_ID,
                filename=ENSEMBLE_MODEL_FILENAME,
                cache_dir=ENSEMBLE_MODEL_DIR,
            )

            logging.info("Ensemble model downloaded.")
            self.model = joblib.load(model_path)
            logging.info("Ensemble model loaded successfully.")

        except Exception as e:
            logging.error(f"[EnsemblePricer] Failed during setup: {e}")
            raise RuntimeError("[EnsemblePricer] Setup failed.") from e

    @modal.method()
    def price(self, ft: float, rag: float, xgb: float) -> float:
        """Predicts final price using ensemble of 3 models."""
        try:
            # Lazy load pandas and numpy for feature creation
            import numpy as np
            import pandas as pd

            features = pd.DataFrame(
                {
                    "FT_LLaMA": [ft],
                    "GPT4oMini": [rag],
                    "XGBoost": [xgb],
                    "Max": [max(ft, rag, xgb)],
                    "Mean": [np.mean([ft, rag, xgb])],
                }
            )
            prediction = self.model.predict(features)[0]
            return round(float(prediction), 2)
        except Exception as e:
            logging.error(f"[EnsemblePricer] Prediction failed: {e}")
            return 0.0
