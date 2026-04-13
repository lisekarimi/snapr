"""Entry point for the application."""

import os

import gradio as gr
import uvicorn
from fastapi import FastAPI

from src.ui.gradio_app import build_ui

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

demo = build_ui()
app = gr.mount_gradio_app(app, demo, path="")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
