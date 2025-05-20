"""Entry point for the application."""

from src.ui.gradio_app import build_ui

if __name__ == "__main__":
    demo_app = build_ui()
    demo_app.launch(server_name="0.0.0.0", server_port=7860)
