"""Predicts prices using XGBoost and E5 embeddings."""

import logging

import modal

from src.modal_services.app_config import (
    CACHE_PATH,
    app,
    modal_class_kwargs,
)
from src.modal_services.e5_model_base import E5ModelBase

REPO_ID = "lisekarimi/smart-deal-finder-models"

# Local paths inside Modal volume
E5_MODEL_DIR = f"{CACHE_PATH}/e5_model"
XGB_MODEL_DIR = f"{CACHE_PATH}/xgb_model"
XGB_MODEL_FILENAME = "xgboost_model.pkl"


@app.cls(**modal_class_kwargs)
class XGBPricer(E5ModelBase):
    """Remote pricing via E5 and XGBoost."""

    @modal.enter()
    def setup(self) -> None:
        """Loads E5 and XGBoost into Modal cache."""
        try:
            # Setup E5 model using the base class method
            self.setup_e5_model()

            # Lazy load XGBoost model and download it inside the setup method
            import joblib
            from huggingface_hub import hf_hub_download

            logging.info("Downloading XGBoost model...")
            model_path = hf_hub_download(
                repo_id=REPO_ID, filename=XGB_MODEL_FILENAME, cache_dir=XGB_MODEL_DIR
            )

            logging.info("XGBoost model downloaded.")
            self.model = joblib.load(model_path)
            logging.info("XGBoost model loaded.")

        except Exception as e:
            logging.error(f"[XGBPricer] Failed during setup: {e}")
            raise RuntimeError("[XGBPricer] Setup failed.") from e

    @modal.method()
    def price(self, description: str) -> float:
        """Predict price from product description using E5 + XGBoost."""
        try:
            logging.info("[XGBPricer] Encoding description...")
            vector = self.vectorizer.encode(["passage: " + description])
            pred = self.model.predict(vector)[0]
            logging.info(f"[XGBPricer] Predicted price: {pred}")
            return round(float(max(0, pred)), 2)
        except Exception as e:
            logging.error(f"[XGBPricer] Failed to predict price: {e}")
            return 0.0
