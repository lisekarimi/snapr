## 🏷️ [0.3.0]

### ✨ Added
- Landing page with favicon
- `app_port: 8080` in HF Space README frontmatter — fixes Space stuck in "building/starting" state

### ♻️ Changed
- MkDocs docs decoupled from FastAPI and moved to GitHub Pages (standalone deployment)
- Simplified FastAPI app init: removed MkDocs mounting and static file routing from `main.py`
- Dockerfile updated: switched to `uv` for dependency management, removed nginx, cleaner layer caching
- Removed chatbot widget (PageBotAI / ChatBot integration)
- Updated repository URLs and `.dockerignore`

### 🗑️ Removed
- MkDocs served via FastAPI (`/docs` endpoint) — now a separate GitHub Pages site
- Hero landing page (replaced by dedicated landing page)

---

## 🏷️ [0.2.0]

### ✨ Added
- FastAPI integration for unified app routing
- MkDocs documentation served at `/docs` endpoint
- Single-container deployment with FastAPI/Uvicorn
- ChatBot widget integration for enhanced user interaction


## 🏷️ [0.1.0]

### ✨ Added
- Modular price prediction agents (FTPriceAgent, RAGPriceAgent, XGBoostPriceAgent, EnsemblePriceAgent)
- DealScannerAgent with memory handling
- PlanningAgent for execution coordination
- Modal deployment for all agents
- Unit tests for price prediction agents
- Currency support and conversion
- Timezone support and unified state logic
- Demo mode with daily run limit
- Persistent deal memory across sessions
- Agent refactoring to support persistent memory
- Gradio UI
- Functional and technical documentation
