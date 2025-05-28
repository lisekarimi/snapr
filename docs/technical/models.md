# 🧠 Machine Learning Models

This section details the models used for price prediction in {{ PROJECT_NAME_DISPLAY }}.

---

## Fine-Tuned LLaMA Model

We fine-tuned a **`LLaMA 3.1 8B Quantized`** model using **`QLoRA`**  on a curated subset (~400K items) from a larger dataset.

🔗 See [Data Pipeline](data.md) for dataset source and preprocessing steps.

After fine-tuning and evaluation, the best-performing checkpoint was published to **Hugging Face Hub**.

📓 Related Notebooks:

- ⚙️ [Fine-Tuning QLoRA](https://github.com/{{ HF_USERNAME }}/{{ PROJECT_NAME }}/blob/main/notebooks/03_ft_llama_qlora.ipynb)
- 📊 [Evaluation Results](https://github.com/{{ HF_USERNAME }}/{{ PROJECT_NAME }}/blob/main/notebooks/04_eval_llama_qlora.ipynb)

At runtime, Modal pulls the model from Hugging Face on first use, caches it, and uses it for zero-shot product price prediction.

---

## XGBoost Model

We reused the same curated dataset to generate embeddings using the **E5 model**, and stored them in a **ChromaDB**, which was uploaded to **AWS S3** for remote access.

Using these embeddings, we trained an **XGBoost regression model** with tuned hyperparameters to predict product prices from vectorized descriptions in the training dataset. The trained model (`xgboost_model.pkl`) was pushed to **Hugging Face Hub**.

The implementation details are documented in [the following notebook](https://github.com/{{ HF_USERNAME }}/{{ PROJECT_NAME }}/blob/main/notebooks/02_e5_xgboost.ipynb)

At runtime, **Modal** pulls:

* the XGBoost model from Hugging Face,
* the E5 embedding model (from `sentence-transformers` on Hugging Face),
* and the ChromaDB from AWS S3.

All components are cached in Modal’s persistent volume after first use for fast, repeatable access.

---

## RAG Pipeline

We also use the **ChromaDB** with **E5 embeddings** to power a **RAG pipeline** for price prediction.

* **Retrieval**: Given a product description, we embed it using the E5 model and retrieve the **top 5 most similar items** from ChromaDB. Each retrieved item includes its description and actual price.

* **Augmented**: The retrieved similar items and their prices are combined with the original product description to form the input context, which **augments** the prompt sent to the language model for price prediction.

* **Generation**: The full prompt — containing the product description and similar item data — is sent to **GPT** via the OpenAI API. The model is instructed to output only the estimated price.

---

## Ensemble Model

After obtaining individual price predictions from the three independent models on the **curated dataset**, we trained a **linear regression model** to combine their outputs.

The model uses the raw predictions along with simple engineered features (e.g., `max`, `mean`) to generate a more stable final estimate.

Once trained and evaluated, the ensemble model (`ensemble_model.pkl`) was pushed to Hugging Face Hub.

📓 [Related Notebook](https://github.com/{{ HF_USERNAME }}/{{ PROJECT_NAME }}/blob/main/notebooks/05_ensemble_model.ipynb)

At runtime, Modal pulls the model from Hugging Face (on first use) and caches it in a persistent volume for efficient reuse during future predictions.

---

## Frontier Model (OpenAI)

We use `OpenAI GPT`to:

- Select the top 5 deals from raw inputs, ensuring clear descriptions and explicit prices, and 
- Estimate product prices after retrieving similar items from ChromaDB for contextual grounding via RAG.