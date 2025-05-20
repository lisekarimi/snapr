"""Predicts item prices using RAG (Retrieval Augmented Generation).

With ChromaDB, E5 embeddings, and GPT-4o-mini.
"""

# Standard library imports
import logging
import os
import zipfile

import modal

# Third-party imports
import numpy as np
import requests

# Local imports
from src.modal_services.app_config import CACHE_PATH, app, modal_class_kwargs
from src.modal_services.e5_model_base import E5ModelBase
from src.models.frontier_model import OPENAI_MODEL
from src.utils.text_utils import extract_price

# Configure logging after all imports
logging.basicConfig(level=logging.INFO)

# Paths
E5_MODEL_DIR = f"{CACHE_PATH}/e5_model"
CHROMA_DIR = f"{CACHE_PATH}/chroma"
CHROMA_ZIP_URL = "https://aiprojects-lise-karimi.s3.eu-west-3.amazonaws.com/smart-deal-finder/chroma.zip"
COLLECTION_NAME = "price_items"


@app.cls(**modal_class_kwargs)
class RAGPricer(E5ModelBase):
    """Remote class for pricing products using RAG pipeline."""

    @modal.enter()
    def setup(self) -> None:
        """Load E5 embedding model, ChromaDB and OpenAI client."""
        try:
            # Lazy load the required modules
            import chromadb

            # Setup E5 model using the base class method
            self.setup_e5_model()

            # ChromaDB setup remains the same
            if not os.path.exists(CHROMA_DIR):
                os.makedirs(CHROMA_DIR, exist_ok=True)
                r = requests.get(CHROMA_ZIP_URL)
                with open("/tmp/chroma.zip", "wb") as f:
                    f.write(r.content)
                with zipfile.ZipFile("/tmp/chroma.zip", "r") as zip_ref:
                    zip_ref.extractall(CHROMA_DIR)
            logging.info("ChromaDB ready.")

            self.chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
            self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME)
            logging.info("ChromaDB client ready.")

        except Exception as e:
            logging.error(f"[RAGPricer] Failed during setup: {e}")
            raise RuntimeError("[RAGPricer] Setup failed.") from e

    def _get_embedding(self, item: str) -> np.ndarray:
        """Encodes the item description into embeddings using the E5 model."""
        return self.vectorizer.encode(["passage: " + item], normalize_embeddings=True)

    def _find_similar_items(self, item: str) -> tuple[list[str], list[float]]:
        """Finds similar items from ChromaDB based on embeddings."""
        query_emb = self._get_embedding(item).astype(float).tolist()
        results = self.collection.query(query_embeddings=query_emb, n_results=5)
        documents = results["documents"][0][:]
        prices = [m["price"] for m in results["metadatas"][0][:]]

        # Log similar items and their prices
        for doc, price in zip(documents, prices):
            logging.info(f"[RAGPricer] Similar item: '{doc}' | Price: ${price:.2f}")

        return documents, prices

    def _format_context(self, similars: list[str], prices: list[float]) -> str:
        """Formats the context for the RAG pipeline."""
        message = "To provide some context, here are some other items "
        message += "that might be similar to the item you need to estimate.\n\n"

        for similar, price in zip(similars, prices):
            message += (
                f"Potentially related product:\n{similar}\nPrice is ${price:.2f}\n\n"
            )

        return message

    def _build_messages(
        self, item: dict, similars: list[str], prices: list[float]
    ) -> list[dict[str, str]]:
        """Builds messages for the GPT-4o-mini model to predict the price."""
        system_message = (
            "You are a pricing expert. "
            "Given a product description and a few similar products with their prices, "
            "you must estimate the most likely price for the given product. "
            "Always respond ONLY with a number, no words or explanation."
        )
        context = self._format_context(similars, prices)
        user_prompt = (
            "Estimate the price for the following product:\n\n"
            + item["description"]
            + "\n\n"
            + context
        )

        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": "Price is $"},
        ]

    @modal.method()
    def price(self, description: str) -> float:
        """Predicts price from description using RAG and Frontier."""
        try:
            logging.info("[RAGPricer] Searching similar items...")
            documents, prices = self._find_similar_items(description)
            messages = self._build_messages(
                {"description": description}, documents, prices
            )

            # Lazy import OpenAI API
            import openai

            response = openai.chat.completions.create(
                model=OPENAI_MODEL, messages=messages, seed=42, max_tokens=5
            )
            reply = response.choices[0].message.content
            price = extract_price(reply)

            logging.info(f"[RAGPricer] Predicted price: {price}")
            return price
        except Exception as e:
            logging.error(f"[RAGPricer] Failed to predict price: {e}")
            return 0.0
