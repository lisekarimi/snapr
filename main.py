"""Entry point for the application."""

import os
import subprocess
from pathlib import Path

import gradio as gr
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.ui.gradio_app import build_ui

# Create FastAPI app with docs completely disabled
app = FastAPI(
    docs_url=None,  # Disable /docs
    redoc_url=None,  # Disable /redoc
    openapi_url=None,  # Disable /openapi.json
)

# Build MkDocs site (creates site/ directory with static HTML)
print("📚 Building MkDocs site...")
try:
    subprocess.run(["mkdocs", "build", "--clean"], check=True)
    print("✅ MkDocs site built successfully")
except subprocess.CalledProcessError as e:
    print(f"⚠️ Failed to build MkDocs: {e}")

# Path to built MkDocs site
site_path = Path(__file__).parent / "site"


# Redirect /docs to /docs/
@app.get("/docs")
async def redirect_to_docs():
    """Redirect /docs to /docs/ for proper routing."""
    return RedirectResponse(url="/docs/")


# Mount MkDocs static site at /docs
if site_path.exists():
    app.mount("/docs", StaticFiles(directory=str(site_path), html=True), name="docs")
    print("✅ MkDocs mounted at /docs")
else:
    print(f"⚠️ Warning: {site_path} not found. Documentation will not be available.")

# Build Gradio UI
print("🎨 Building Gradio UI...")
demo = build_ui()

# Mount Gradio app at root - use empty string instead of "/"
app = gr.mount_gradio_app(app, demo, path="")
print("✅ Gradio mounted at root")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    uvicorn.run(app, host="0.0.0.0", port=port)
