"""Executes planning agent and streams logs/results.

Integrates with the Gradio UI.
"""

import queue
import threading
import time
import traceback
from typing import Any, Generator, List, Optional, Tuple, Union

import gradio as gr

from src.agents.planning_agent import PlanningAgent
from src.config.constants import (
    DEALS_FILE,
    IS_DEMO_VERSION,
    MAX_CATEGORY_SELECTION,
)
from src.config.logging_queue import log_queue
from src.ui.formatting import format_deals_table, html_for
from src.utils.cleanup import delete_if_old
from src.utils.state_manager import can_run_app, get_state, update_state


def run_pipeline(log_queue: queue.Queue, selected_categories: List[str]) -> None:
    """Runs the planning agent pipeline and stores accepted deals."""
    try:
        delete_if_old(DEALS_FILE)
        agent = PlanningAgent()
        results = agent.plan(selected_categories)

        global accepted_deals
        accepted_deals = [
            [
                opp.product_description,
                f"${opp.price:.2f}",
                f"${opp.estimate:.2f}",
                f"${opp.discount:.2f}",
                opp.url,
            ]
            for opp in results
        ]

    except Exception as e:
        log_queue.put(
            f"<span style='color:red'>❌ Error during pipeline execution: "
            f"{str(e)}</span>"
        )
        log_queue.put(f"<pre>{traceback.format_exc()}</pre>")


def validate_categories(
    selected_categories: Union[str, List[str]],
) -> Tuple[bool, Optional[str]]:
    """Validates the selected categories."""
    if isinstance(selected_categories, str):
        selected_categories = [selected_categories]

    if not selected_categories:
        return False, "⚠️ Please select at least one category before running."

    if len(selected_categories) > MAX_CATEGORY_SELECTION:
        return (
            False,
            f"⚠️ You can select up to {MAX_CATEGORY_SELECTION} categories only.",
        )

    return True, None


def check_demo_restrictions() -> Tuple[bool, Optional[str], Optional[str]]:
    """Checks if the app can run under demo restrictions."""
    can_run, message = can_run_app()

    if not can_run:
        return False, f"⚠️ {message}", None

    if IS_DEMO_VERSION:
        # Just update the run count, but use the message from can_run_app
        update_state({"run_count": get_state()["run_count"] + 1})
        # Get fresh message after updating the state
        _, status_msg = can_run_app()
    else:
        status_msg = ""

    return True, None, status_msg


def initial_ui_update(
    log_data: List[str], status_msg: str
) -> Tuple[str, str, Any, str]:
    """Returns initial UI state for the app."""
    disable_btn = gr.update(
        interactive=False, elem_classes=["run-button", "btn-disabled"]
    )
    return html_for(log_data), format_deals_table([]), disable_btn, status_msg


def run_pipeline_threaded(
    selected_categories: List[str],
    log_data: List[str],
    status_msg: str,
    enable_btn: Any,  # noqa: ANN401
) -> Generator[Tuple[str, str, Any, str], None, None]:
    """Runs pipeline in background thread with log streaming.

    Yields UI updates until completion.

    """
    thread = threading.Thread(
        target=run_pipeline, args=(log_queue, selected_categories)
    )
    thread.start()

    disable_btn = gr.update(
        interactive=False, elem_classes=["run-button", "btn-disabled"]
    )

    while thread.is_alive() or not log_queue.empty():
        while not log_queue.empty():
            log_msg = log_queue.get()
            log_data.append(log_msg)
            yield (
                html_for(log_data),
                format_deals_table(accepted_deals),
                disable_btn,
                status_msg,
            )

        if thread.is_alive():
            time.sleep(0.2)
            yield (
                html_for(log_data),
                format_deals_table(accepted_deals),
                disable_btn,
                status_msg,
            )

    # Final UI update after thread finishes
    yield html_for(log_data), format_deals_table(accepted_deals), enable_btn, status_msg


def handle_pipeline_error(
    e: Exception,
    log_data: List[str],
    enable_btn: gr.components.Component,
    status_msg: str,
) -> Tuple[str, str, gr.components.Component, str]:
    """Handles exceptions and appends error logs.

    Returns the final UI update tuple.
    """
    log_data.append(f"<span style='color:red'>❌ Unexpected error: {str(e)}</span>")
    log_data.append(f"<pre>{traceback.format_exc()}</pre>")
    return html_for(log_data), format_deals_table([]), enable_btn, status_msg


def run_and_stream_logs(
    selected_categories: Union[str, List[str]],
) -> Generator[Tuple[str, str, bool, str], None, None]:
    """Runs pipeline in a thread, streaming logs and results to the UI.

    Returns HTML logs, deal table, button state, and status message.
    """
    global accepted_deals
    accepted_deals = []
    log_data = []

    # Step 1: Validate categories
    is_valid, error_msg = validate_categories(selected_categories)
    if not is_valid:
        yield None, None, gr.update(interactive=True), error_msg
        return

    # Step 2: Check demo restrictions
    can_run, error_msg, status_msg = check_demo_restrictions()
    if not can_run:
        yield (
            html_for([error_msg]),
            format_deals_table([]),
            gr.update(interactive=True),
            error_msg,
        )
        return

    # Step 3: Initial UI update showing we're starting
    enable_btn = gr.update(interactive=True, elem_classes=["run-button"])
    yield initial_ui_update(log_data, status_msg)

    try:
        # Step 4: Run the pipeline in a thread
        yield from run_pipeline_threaded(
            selected_categories, log_data, status_msg, enable_btn
        )

    except Exception as e:
        yield handle_pipeline_error(e, log_data, enable_btn, status_msg)
