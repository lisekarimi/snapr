# 🏷️ Snapr - Multi-AI Agent Snaps Best Deals

- [🚀 Live Demo](https://snapr.lisekarimi.com)
- [📚 Full Documentation](https://snapr.lisekarimi.com/docs)

📷 **Screenshots**

<img src="https://github.com/lisekarimi/snapr/blob/main/docs/styles/assets/ui/full_app.png?raw=true" alt="Snapr interface" width="400">

## 📖 Overview
**Snapr** is an AI-powered system that finds the best online deals using a pipeline of collaborative agents powered by LLMs, traditional ML models, embeddings, and retrieval-augmented generation (RAG).

### 🔑 Key Capabilities
- Central agent orchestrates deal processing with specialized agents
- Real-time deal fetching and price prediction using LLMs and traditional models
- Automatic filtering and memory to avoid duplicates
- Remote execution on Modal with live activity logs
- DevOps: Docker, CI/CD with GitHub Actions, pre-commit hooks
- Unit testing, security checks, and code quality enforcement
- MkDocs-based documentation

👉 For full details, see [Core Features and Development & DevOps.](https://snapr.lisekarimi.com/docs).

## ⚙️ Setup & Installation

To set up locally and install the app, see the "Local Deployment" section in the [technical documentation](https://snapr.lisekarimi.com/docs/technical/localdev/).

### 🏗️ Architecture
- **Single Container Deployment**: FastAPI serves both the Gradio app and documentation
  - Main app at `/` - Interactive Gradio interface
  - Documentation at `/docs` - MkDocs static site
  - No reverse proxy needed - everything runs through uvicorn/FastAPI
- Containerized with Docker for consistent deployment across environments

## 📚 Docs & Architecture

- Documentation includes:

    - Technical and functional docs
    - Schematics of technical architecture, functional workflow, and user flow

## 🪪 License

MIT
