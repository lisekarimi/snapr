# ✨ Features

This section highlights {{ PROJECT_NAME_DISPLAY }}’s core features and agents — from category selection to finding the best-value deals through smart discovery and filtering.

![](../styles/assets/features.png)
*Click on image to zoom*

## 🧠 Planning Agent

- Orchestrates the full pipeline: 
    - Scans deals via DealScannerAgent, 
    - Predicts prices using multiple agents (`FTPriceAgent`, `XGBoostPriceAgent`, `RAGPriceAgent`, `EnsemblePriceAgent`)
    - Filters deals based on a fixed discount threshold
    - And saves accepted deals to shared memory.
- Logs each decision for transparency.
- Produces a structured summary of accepted deals with price, estimated value, discount, and link.

## 🟢 Deal Scanner Agent

- Fetches real-time deals from RSS feeds based on selected categories.
- Already-seen deals are automatically skipped using a memory system.
- `OpenAI (GPT)` selects the top 5 deals by filtering for clear descriptions and exact numeric prices.
- Results are returned in a consistent, machine-readable `JSON format`.
- Users can view real-time logs of what the agent is doing (e.g., fetched deals, skipped, filtered).

## 🔴 Fine-Tuned LLM Agent

- Uses a `fine-tuned (FT) LLaMA` model to predict prices from product descriptions.
- Runs remotely on `Modal` for scalable execution.
- Provides logs on remote calls and failures.

## 🔵 RAG-Based Agent

- Predicts prices using a Retrieval-Augmented Generation pipeline.
- Combines E5 embeddings, ChromaDB, and a frontier LLM (`OpenAI GPT`).
- Executes remotely via `Modal` and logs embedding/model activity.

## 🟡 XGBoost-Based Agent

- Uses `E5 embeddings` + `XGBoost` for regression-based price prediction.
- Runs remotely on `Modal` infrastructure.
- Logs model loading and predictions visibly.

## 🟣 Ensemble Agent

- Combines predictions from `FT`, `RAG`, and `XGBoost` agents.
- Applies a trained `linear regression model` to produce a final estimated price.
- Logs individual predictions and final computed result.

