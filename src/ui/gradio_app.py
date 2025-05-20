"""Launches a Gradio app that runs an AI planning agent to find smart online deals.

Uses Python's built-in logging system for consistent logs.
Includes demo mode restrictions: MAX_DEMO_RUNS_PER_DAY runs per day.
"""

import os
from typing import Tuple

import gradio as gr
from dotenv import load_dotenv

from src.agents.pipeline import run_and_stream_logs
from src.config.constants import (
    IS_DEMO_VERSION,
    MAX_CATEGORY_SELECTION,
    MAX_DEMO_RUNS_PER_DAY,
)
from src.config.feeds import CATEGORY_FEEDS
from src.ui.formatting import format_deals_table
from src.utils.logger import console
from src.utils.state_manager import can_run_app
from src.version import __version__

load_dotenv(dotenv_path="src/config/deploy.env")
project_name = os.getenv("PROJECT_NAME")
pretty_name = project_name.replace("-", " ").title()

REPO_URL = f"https://github.com/lisekarimi/{project_name}"
DOC_URL = f"https://lisekarimi.github.io/{project_name}"


def build_ui() -> gr.Blocks:
    """Constructs and returns the Gradio UI interface, with error handling."""
    try:
        with open(
            os.path.join(os.path.dirname(__file__), "assets", "styles.css"), "r"
        ) as f:
            css = f.read()
    except Exception as e:
        css = ""
        console.print(f"[bold yellow]⚠️ Failed to load CSS:[/] {e}")

    # Set initial UI state here
    disable_btn = False
    initial_status = "Loading demo status..."

    # Building the UI
    try:
        with gr.Blocks(css=css, title=f"🏷️{pretty_name}") as ui:
            with gr.Column(elem_id="app-container"):
                # 🔝 Top content
                gr.Markdown(f"<h1 id='app-title'>🏷️ {pretty_name} </h1>")
                gr.Markdown(
                    "<h2 id='app-subtitle'>Autonomous AI Agents Snapping the Best "
                    "Deals Online</h2>"
                )
                gr.HTML(
                    f"""
                    <div id="intro-text">
                        <p>🏷️ <strong>Snapr</strong>, 
                        <strong>an Agentic AI System</strong>, 
                        discovers the best online deals for you—smart, 
                        simple, and automatic. 
                        Let <strong>AI</strong> do the work, so you can save money 
                        without any effort.</p>


                        <h4>🤖 How It Works:</h4>
                            <p>1️⃣ Choose up to {MAX_CATEGORY_SELECTION} 
                            categories to search.</p>
                            <p>2️⃣ Click "Find Smart Deals" — AI scans, estimates prices, 
                            and filters top discounts.</p>
                            <p>3️⃣ See the best deals in a table with prices, discounts, 
                            and direct links.</p>
                    </div>
                    """
                )
                if IS_DEMO_VERSION:
                    gr.Markdown(
                        f"""
                        <p>⚠️ This is a demo version — limited to 
                        {MAX_DEMO_RUNS_PER_DAY} global runs per day for all users.</p>
                        """
                    )

                gr.Markdown(
                    f"""
                    <p class="custom-links">📦 Want more?
                    You can <a href="{REPO_URL}" 
                    target="_blank">run it locally</a> 
                    with full <a href="{DOC_URL}/technical/localdev/" 
                    target="_blank">instructions</a> and
                    <a href="{DOC_URL}" 
                    target="_blank">documentation</a>.</p>
                    """
                )

                with gr.Column(elem_id="left-col"):
                    category_selector = gr.Dropdown(
                        choices=list(CATEGORY_FEEDS.keys()),
                        value="Electronics",
                        multiselect=True,
                        label=(
                            f"🧭 Select up to {MAX_CATEGORY_SELECTION} Deal Categories"
                        ),
                        elem_id="category-selector",
                        elem_classes="custom-dropdown",
                    )
                    run_btn = gr.Button(
                        "🔍 Find Smart Deals",
                        elem_id="run-btn",
                        variant="primary",
                        elem_classes="run-button",
                        interactive=not disable_btn,
                    )

                status_msg = gr.HTML(value=initial_status, elem_id="status-message")

                # Logs + deals
                logs_output = gr.HTML(
                    value="""
                    <div id="logs-label">📜 Live Agent Logs</div>
                        <div id="scrollContent">
                            🕵️‍♀️ Click "🔍 Find Smart Deals" to wake the agents and 
                            stream logs here!
                        </div> 
                    """
                )

                deals_output = gr.HTML(
                    value=format_deals_table([]), elem_id="deal-table"
                )

                # Connect button
                run_btn.click(
                    fn=run_and_stream_logs,
                    inputs=[category_selector],
                    outputs=[logs_output, deals_output, run_btn, status_msg],
                )

                # Status update on load
                @ui.load(outputs=[status_msg, run_btn])
                def update_status_on_load() -> Tuple[str, gr.update]:
                    """Sets demo status and button state on UI load."""
                    can_run, status = can_run_app()
                    btn_state = gr.update(
                        interactive=can_run,
                        elem_classes=(
                            ["run-button", "btn-disabled"]
                            if not can_run
                            else ["run-button"]
                        ),
                    )
                    return status, btn_state

            # Bottom: version info
            gr.Markdown(
                f"""
                <p class="version-banner">
                    🔖 <strong>
                    <a href="{DOC_URL}/changelog" 
                    target="_blank">Version {__version__}</a>
                    </strong>
                </p>
                """
            )

        return ui

    except Exception as e:
        console.print(f"[bold red]❌ Failed to build UI:[/] {e}")
        raise
