"""Test module for XGBoostPriceAgent."""

from unittest.mock import MagicMock, patch

import pytest

from src.agents.xgb_price_agent import XGBoostPriceAgent
from src.modal_services.app_config import APP_NAME


@pytest.fixture
def mock_modal():
    """Mocks Modal remote class."""
    with patch("modal.Cls.from_name") as mock_from_name:
        mock_remote_cls = MagicMock()
        mock_from_name.return_value = mock_remote_cls
        yield mock_from_name, mock_remote_cls


@pytest.fixture
def agent(mock_modal):
    """Returns an agent with mocked remote."""
    with patch.object(XGBoostPriceAgent, "log") as mock_log:
        agent = XGBoostPriceAgent()
        yield agent, mock_log


def test_initialization(agent, mock_modal):
    """Tests the agent initialization process."""
    agent_instance, mock_log = agent
    mock_from_name, _ = mock_modal

    # Ensure the XGBoost component was initialized
    assert agent_instance.xgb is not None

    # Check that the correct remote class was loaded via Modal
    mock_from_name.assert_called_once_with(APP_NAME, "XGBPricer")

    # Confirm that a log message was emitted during initialization
    mock_log.assert_called()


def test_price_success(agent):
    """Mocks a valid price prediction."""
    agent_instance, _ = agent  # Unpack the agent instance
    agent_instance.xgb.price.remote = MagicMock(return_value=42.99)

    result = agent_instance.price("Test description")
    assert result == 42.99
    agent_instance.xgb.price.remote.assert_called_once_with("Test description")


def test_price_remote_exception():
    """Simulates a remote failure."""
    with patch("modal.Cls.from_name") as mock_from_name:
        # Set up the mock instance
        mock_cls = MagicMock()
        mock_instance = MagicMock()

        mock_from_name.return_value = mock_cls
        mock_cls.return_value = mock_instance

        mock_instance.price.remote.side_effect = Exception("Modal error")

        # Create agent with our mocked instance
        agent = XGBoostPriceAgent()

        # Now test the exception handling
        with pytest.raises(
            RuntimeError, match="XGBoostPriceAgent failed to get price from Modal"
        ):
            agent.price("Error case")
