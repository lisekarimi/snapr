"""Unit tests for EnsemblePriceAgent.

Calls a remote Modal class to predict final prices.
"""

from unittest.mock import MagicMock, call, patch

import pytest

from src.agents.ensemble_price_agent import EnsemblePriceAgent
from src.modal_services.app_config import APP_NAME


@pytest.fixture
def mock_modal():
    """Fixture that mocks the Modal remote class instantiation."""
    with patch("modal.Cls.from_name") as mock_from_name:
        mock_remote_instance = MagicMock()
        mock_remote_cls = MagicMock(return_value=mock_remote_instance)
        mock_from_name.return_value = mock_remote_cls
        yield mock_from_name, mock_remote_instance


@pytest.fixture
def agent(mock_modal):
    """Fixture returning a mocked EnsemblePriceAgent with patched logging."""
    with patch.object(EnsemblePriceAgent, "log") as mock_log:
        agent = EnsemblePriceAgent()
        yield agent, mock_log


def test_initialization(agent, mock_modal):
    """Tests that agent initializes and connects to the correct Modal class."""
    agent_instance, mock_log = agent
    mock_from_name, _ = mock_modal
    assert call(APP_NAME, "EnsemblePricer") in mock_from_name.call_args_list
    mock_log.assert_called()


def test_price_success(agent):
    """Tests that agent returns predicted price from remote call."""
    agent_instance, _ = agent
    expected_price = 123.45

    # Mock sub-agent predictions
    with (
        patch.object(agent_instance, "ft_agent") as mock_ft,
        patch.object(agent_instance, "rag_agent") as mock_rag,
        patch.object(agent_instance, "xgb_agent") as mock_xgb,
    ):
        mock_ft.price.return_value = 100.0
        mock_rag.price.return_value = 120.0
        mock_xgb.price.return_value = 130.0

        # Mock remote ensemble call
        agent_instance.ensemble.price.remote = MagicMock(return_value=expected_price)

        # Call price method with a sample description
        result = agent_instance.price("Test description")

        assert result == expected_price
        agent_instance.ensemble.price.remote.assert_called_once_with(
            100.0, 120.0, 130.0
        )


def test_price_remote_exception(mock_modal):
    """Tests that the agent raises a RuntimeError if the remote Modal call fails."""
    mock_from_name, mock_remote_instance = mock_modal
    mock_remote_instance.price.remote.side_effect = Exception("Modal failed")

    with patch.object(EnsemblePriceAgent, "log") as mock_log:
        agent = EnsemblePriceAgent()

        # Mock sub-agent predictions
        with (
            patch.object(agent, "ft_agent") as mock_ft,
            patch.object(agent, "rag_agent") as mock_rag,
            patch.object(agent, "xgb_agent") as mock_xgb,
        ):
            mock_ft.price.return_value = 100.0
            mock_rag.price.return_value = 200.0
            mock_xgb.price.return_value = 300.0

            with pytest.raises(RuntimeError) as excinfo:
                agent.price("Failing description")

            assert "EnsemblePriceAgent failed to get final price." in str(excinfo.value)
            mock_log.assert_any_call(
                "[ERROR] Remote EnsemblePricer failed: Modal failed"
            )
