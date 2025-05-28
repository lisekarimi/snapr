"""Entry point for the application."""

from src.ui.gradio_app import build_ui

demo = build_ui()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
