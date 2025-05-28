"""Defines Pricer agent using fine-tuned LLaMA on Modal."""

import logging
import os
from typing import Any

import modal

from src.modal_services.app_config import CACHE_PATH, app, modal_class_kwargs
from src.utils.text_utils import extract_tagged_price

logging.basicConfig(level=logging.INFO)

# Model identifiers
BASE_MODEL = "meta-llama/Meta-Llama-3.1-8B"
FINETUNED_MODEL = "ed-donner/pricer-2024-09-13_13.04.39"
REVISION = "e8d637df551603dc86cd7a1598a8f44af4d7ae36"

# Local model paths in volume
BASE_MODEL_DIR = f"{CACHE_PATH}/llama_base_model"
FINETUNED_MODEL_DIR = f"{CACHE_PATH}/llama_finetuned_model"

QUESTION = "How much does this cost to the nearest dollar?"
PREFIX = "Price is $"


@app.cls(**modal_class_kwargs)
class FTPricer:
    """Remote pricing with LLaMA, PEFT, and 4-bit quantization."""

    @staticmethod
    def _build_prompt(description: str) -> str:
        return f"{QUESTION}\n\n{description}\n\n{PREFIX}"

    @staticmethod
    def _generate_output(
        model: Any,  # noqa: ANN401
        inputs: dict,
        tokenizer: Any,  # noqa: ANN401
    ) -> str:
        """Generate output from model."""
        import torch

        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=5, num_return_sequences=1)
        return tokenizer.decode(outputs[0])

    @staticmethod
    def _download_models() -> None:
        from huggingface_hub import snapshot_download

        snapshot_download(BASE_MODEL, local_dir=BASE_MODEL_DIR)
        snapshot_download(
            FINETUNED_MODEL, revision=REVISION, local_dir=FINETUNED_MODEL_DIR
        )

    def _load_tokenizer(self) -> None:
        from transformers import AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_DIR)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        logging.info("Tokenizer loaded.")

    def _load_models(self) -> None:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, BitsAndBytesConfig

        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_DIR,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4",
            ),
            device_map="auto",
        )

        self.fine_tuned_model = PeftModel.from_pretrained(
            base_model, FINETUNED_MODEL_DIR, revision=REVISION
        )
        self.fine_tuned_model.eval()
        gen_config = self.fine_tuned_model.generation_config
        gen_config.pad_token_id = self.tokenizer.pad_token_id
        gen_config.eos_token_id = self.tokenizer.eos_token_id
        logging.info("Models loaded.")

    @modal.enter()
    def setup(self) -> None:
        """Load base and fine-tuned models with tokenizer and quantization."""
        try:
            os.makedirs(CACHE_PATH, exist_ok=True)
            self._download_models()
            logging.info("Base and fine-tuned models downloaded.")
            self._load_tokenizer()
            self._load_models()
        except Exception as e:
            logging.error(f"[FTPricer] Setup failed: {e}")
            raise RuntimeError("[FTPricer] Model setup failed") from e

    @modal.method()
    def price(self, description: str) -> float:
        """Generate a price estimate based on a product description."""
        from transformers import set_seed

        try:
            set_seed(42)
            logging.info("[FTPricer] Generating price...")

            prompt = self._build_prompt(description)
            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True).to(
                "cuda"
            )
            result = self._generate_output(
                self.fine_tuned_model, inputs, self.tokenizer
            )
            price = extract_tagged_price(result)

            logging.info(f"[FTPricer] Predicted price: {price}")
            return price

        except Exception as e:
            logging.error(f"[FTPricer] Prediction failed: {e}")
            return 0.0
