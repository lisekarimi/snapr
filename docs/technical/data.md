# 🗂️ Dataset & Curation

{{ PRETTY_PROJECT_NAME }}’s training data was sourced, filtered, cleaned, embedded, and sampled at scale. This section documents the entire process.

📓 Related Notebooks:

- ⚙️ [Data Curation](https://github.com/{{ HF_USERNAME }}/{{ PROJECT_NAME }}/blob/main/notebooks/01_data_curation.ipynb)
- 📊 [Embeddings & ChromaDB](https://github.com/{{ HF_USERNAME }}/{{ PROJECT_NAME }}/blob/main/notebooks/02_e5_xgboost.ipynb)

---

## 🔗 Source

We used the [Amazon Reviews 2023 dataset](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) by McAuley Lab — a large-scale dataset of 2,811,408 items — focusing on 8 product categories:

- Automotive
- Electronics
- Office Products
- Tools & Home Improvement
- Cell Phones & Accessories
- Toys & Games
- Appliances
- Musical Instruments

Each product entry includes metadata such as price, title, description, and features.

---

## 🧹 Filtering Logic

Items were filtered using the following rules:

- **Price range**: $0.50 ≤ price ≤ $999.49
- **Minimum text length**: ≥ 300 characters
- **Tokenized prompt length**: 150–160 tokens measured using the LLaMA tokenizer, chosen because it handles numeric values (e.g., 123) as a single token — making token estimation more stable and convenient for our use case.
- **Noise removal**: Stripped boilerplate phrases and irrelevant product codes

---

## 🔄 Sampling Strategy

To ensure a balanced dataset:

- All items were kept if:
    - Price ≥ $240  
    - Group size (by rounded price) ≤ 1200
- Otherwise:
    - Sampled up to 1200 items per price group
    - Gave 5× weight to rare categories, 1× to overrepresented ones (e.g., Automotive)

Final curated dataset size: **409,172** items

---

## 🧪 Train/Test Split

The dataset was randomly shuffled with `seed=42`:

- **Train set**: 400,000 items  
- **Test set**: 2,000 items

Used primarily to train and evaluate the fine-tuned LLaMA model.

---

## ☁️ Storage & Hosting

The final dataset is pushed to the Hugging Face Hub:

[https://huggingface.co/datasets/{{ HF_USERNAME }}/pricer-data](https://huggingface.co/datasets/{{ HF_USERNAME }}/pricer-data)

---

## 🔍 Embeddings & ChromaDB

We used the **intfloat/e5-small-v2** model to embed all product descriptions:

- **"passage:"** prefix applied for each input  
- Embeddings were stored in **ChromaDB** (hosted on AWS)
- Used for:
    - Retrieval in the **RAG pipeline**
    - Feature vectors in **XGBoost** model training



