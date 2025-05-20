"""Unit tests for the pipeline module."""

from unittest.mock import Mock, patch

from src.agents import pipeline
from src.agents.pipeline import validate_categories
from src.config.constants import MAX_CATEGORY_SELECTION


def test_validate_categories_none_selected():
    """Tests that validation fails when no categories are selected."""
    valid, msg = validate_categories([])
    assert not valid
    assert "at least one category" in msg


def test_validate_categories_too_many():
    """Tests that validation fails when too many categories are selected."""
    categories = [f"cat{i}" for i in range(MAX_CATEGORY_SELECTION + 1)]
    valid, msg = validate_categories(categories)
    assert not valid
    assert "up to" in msg


def test_validate_categories_valid():
    """Tests that validation passes with a valid number of categories."""
    categories = ["tech", "books"]
    valid, msg = validate_categories(categories)
    assert valid
    assert msg is None


def test_check_demo_restrictions_demo_off():
    """Tests that check_demo_restrictions allows execution when demo mode is off."""
    with (
        patch("src.utils.state_manager.can_run_app", return_value=(True, "")),
        patch("src.agents.pipeline.IS_DEMO_VERSION", False),
    ):
        allowed, err, status = pipeline.check_demo_restrictions()
        assert allowed is True
        assert err is None
        assert status == ""


def test_check_demo_restrictions_demo_on():
    """Tests that demo mode decrements count and returns correct status."""
    # Create a mock that returns different values on successive calls
    can_run_app_mock = Mock(
        side_effect=[(True, ""), (True, "You have 1 run left today")]
    )

    with (
        patch("src.agents.pipeline.can_run_app", can_run_app_mock),
        patch("src.agents.pipeline.IS_DEMO_VERSION", True),
        patch("src.agents.pipeline.get_state", return_value={"run_count": 1}),
        patch("src.agents.pipeline.update_state", return_value={"run_count": 2}),
        patch.object(pipeline, "MAX_DEMO_RUNS_PER_DAY", 3, create=True),
    ):
        allowed, err, status = pipeline.check_demo_restrictions()
        assert allowed is True
        assert err is None
        assert "1 run" in status

        # Verify that can_run_app was called twice
        assert can_run_app_mock.call_count == 2


def test_run_pipeline_success():
    """Tests that run_pipeline handles deals without logging errors."""
    mock_queue = Mock()

    with (
        patch("src.agents.pipeline.delete_if_old"),
        patch("src.agents.pipeline.PlanningAgent") as MockAgent,
    ):
        # Mock PlanningAgent.plan() to return a list with one mock opportunity
        mock_instance = Mock()
        mock_instance.plan.return_value = [
            Mock(
                product_description="Item A",
                price=10,
                estimate=20,
                discount=10,
                url="http://item",
            )
        ]
        MockAgent.return_value = mock_instance

        pipeline.run_pipeline(mock_queue, ["tech"])

        assert isinstance(pipeline.accepted_deals, list)
        assert len(pipeline.accepted_deals) == 1
        assert "Item A" in pipeline.accepted_deals[0][0]
        assert mock_queue.put.call_count == 0


def test_run_pipeline_threaded():
    """Tests that run_pipeline_threaded streams logs and updates the UI."""
    # Patch run_pipeline so it doesn't actually run logic
    with patch("src.agents.pipeline.run_pipeline"):
        # Set up log queue and accepted deals
        pipeline.log_queue.queue.clear()
        pipeline.log_queue.put("Processing...")
        pipeline.accepted_deals = [["desc", "$10", "$20", "$10", "url"]]

        # Call the generator and collect results
        updates = list(
            pipeline.run_pipeline_threaded(
                selected_categories=["tech"],
                log_data=[],
                status_msg="Running...",
                enable_btn="enabled",
            )
        )

        # Assert updates contain expected log output
        assert any("Processing..." in html for html, *_ in updates)
        assert all(isinstance(update, tuple) and len(update) == 4 for update in updates)


def test_handle_pipeline_error():
    """Tests that handle_pipeline_error logs the exception and updates the UI."""
    logs = []

    try:
        raise ValueError("Test Error")
    except Exception as e:
        result = pipeline.handle_pipeline_error(e, logs, "enabled", "status")

    assert "Unexpected error" in result[0]
    assert "<pre>" in result[0]
    assert "ValueError" in result[0]
    assert result[2] == "enabled"
    assert len(logs) == 2
    assert "Test Error" in logs[0]
    assert "ValueError" in logs[1]


def test_run_and_stream_logs_invalid_cat():
    """Tests that invalid category shows error and re-enables button."""
    result = list(pipeline.run_and_stream_logs([]))

    assert result[0][0] is None  # No HTML log
    assert result[0][1] is None  # No deals table
    assert result[0][2]["interactive"] is True  # Button re-enabled
    assert "Please select at least one" in result[0][3]  # Status message


def test_run_and_stream_logs_demo_blocked():
    """Tests that demo restriction blocks the pipeline and updates the UI."""
    with (
        patch("src.agents.pipeline.validate_categories", return_value=(True, None)),
        patch(
            "src.agents.pipeline.check_demo_restrictions",
            return_value=(False, "Blocked", None),
        ),
    ):
        result = list(pipeline.run_and_stream_logs(["tech"]))

        assert "Blocked" in result[0][0]  # Message is in the rendered log
        assert result[0][2]["interactive"] is True
        assert result[0][3] == "Blocked"  # Status message
