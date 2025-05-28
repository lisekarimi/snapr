"""Entry point for creating Modal classes."""

import os

import modal
from dotenv import load_dotenv

from src.modal_services.app_config import app
from src.modal_services.ensemble_pricer import EnsemblePricer
from src.modal_services.ft_pricer import FTPricer
from src.modal_services.rag_pricer import RAGPricer
from src.modal_services.xgb_pricer import XGBPricer

# Load environment variables after imports
load_dotenv()

MODAL_TOKEN_ID = os.getenv("MODAL_TOKEN_ID")
MODAL_TOKEN_SECRET = os.getenv("MODAL_TOKEN_SECRET")

if not MODAL_TOKEN_ID or not MODAL_TOKEN_SECRET:
    raise ValueError("❌ Missing Modal tokens!")

# These imports are required for Modal class registration
__all__ = ["FTPricer", "XGBPricer", "RAGPricer", "EnsemblePricer", "app", "modal"]
