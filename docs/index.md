{{ snippet("_version.md") }}

# 🏷️ {{ PRETTY_PROJECT_NAME }}

**Multi-agent AI system built to find the best deals — so you never overpay.**  
*Smart. Simple. Automatic.*

---

## ✨ Overview

{{ PRETTY_PROJECT_NAME }} is an agentic AI system designed to scan, evaluate, and find the best online deals in real time. It uses several AI models and agents to forecast product prices, spot big discounts, and remove irrelevant deals — so users only see what’s truly worth buying.

---

## 🚀 How It Works

<details>
  <summary>Click to expand the flow</summary>

  <p>1️⃣ Users select up to {{ MAX_CAT }} categories from a predefined list in a sleek Gradio interface.</p>

  <p>2️⃣ A <strong>DealScanner agent</strong> fetches products and uses OpenAI to select the 5 best deals, ensuring clarity in description and pricing.</p>

  <p>3️⃣ Descriptions are passed to three independent agent models, each operating separately:</p>
    <ul>
      <li>A fine-tuned <strong>LLaMA LLM</strong></li>
      <li><strong>XGBoost</strong> with <strong>E5 embeddings</strong></li>
      <li>A <strong>RAG pipeline</strong> using <strong>E5 embeddings</strong> with <strong>ChromaDB</strong> and a frontier <strong>LLM model</strong></li>
    </ul>
  <p>The three agent predictions are combined by an <strong>ensemble agent</strong> using a <strong>linear regression model</strong> to produce the final estimated price.</p>

  <p>4️⃣ If the actual price is at least <strong>${{DEAL_THRESHOLD}} lower</strong> than the final estimated value, the deal is accepted.</p>

  <p>5️⃣ Accepted deals appear in a table with name, prices, discount, and link.</p>

</details>

---

## 🌟 Core Features

- Central agent orchestrates all specialized agents and workflow
- Real-time fetching of deals from RSS feeds
- Advanced price prediction via LLMs (OpenAI, Fine-tuned LLaMA), XGBoost, RAG, and linear regression agents
- Automated deal filtering using a configurable discount threshold
- Transparent logging of all agent actions and decisions
- Structured output with summary data: price, value, discount, and link
- Memory system with shared storage to skip already-seen deals
- Remote execution with scalable, compute-heavy models on Modal
- User-facing live logs with real-time agent activity updates

## 🔧 Development & DevOps

- `.env` files for secure management of API keys and secrets
- PEP8 compliance enforced via Ruff and Black
- Makefile with all essential project commands
- Pre-commit hooks for code quality, security, and dependency consistency
- Environment distinction between production and development
- Docker support for local development and deployment
- CI/CD automation with GitHub Actions for testing, code quality, security checks, and production deployment
- Documentation built with `MkDocs Material`

---

## 🖥️ Demo

> [👉 Try it on Hugging Face Spaces](https://huggingface.co/spaces/{{ HF_USERNAME }}/{{ PROJECT_NAME }})  
> *(Limit: {{ MAX_DEMO_RUNS }} searches per user in demo mode)*

---

## 🛠️ Tech Stack

- **Languages & Frameworks:** Python, Gradio
- **Machine Learning & AI:** OpenAI (GPT), Fine Tuned LLaMA, RAG with E5 embeddings and ChromaDB, XGBoost
- **Deployment & Infrastructure:** Docker, Modal, AWS S3, DockerHub
- **Documentation & Testing:** MkDocs with mkdocs-material, Pytest, Pre-commit hooks
- **DevOps & CI/CD:** GitHub Actions, requirements.lock

---

## 🔗 Useful Links

- [Source Code](https://github.com/{{ HF_USERNAME }}/{{ PROJECT_NAME }})
- [Live App](https://huggingface.co/spaces/{{ HF_USERNAME }}/{{ PROJECT_NAME }})
- [DockerHub](https://hub.docker.com/repository/docker/{{ DOCKER_USERNAME }}/{{ PROJECT_NAME }})

