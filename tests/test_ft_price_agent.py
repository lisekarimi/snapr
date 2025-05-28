"""Test module for FTPriceAgent."""

from unittest.mock import MagicMock, patch

import pytest

from src.agents.ft_price_agent import FTPriceAgent
from src.modal_services.app_config import APP_NAME
from src.utils.text_utils import extract_tagged_price


@pytest.fixture
def mock_pricer_class():
    """Fixture that mocks the remote Modal Pricer class."""
    with patch("modal.Cls.from_name") as mock_from_name:
        mock_instance = MagicMock()
        mock_instance.price.remote.return_value = 42.0  # default mocked return
        mock_from_name.return_value = MagicMock(return_value=mock_instance)
        yield mock_from_name, mock_instance


def test_init_logs_and_connection(mock_pricer_class):
    """Test FTPriceAgent initialization and connection to Modal."""
    mock_from_name, mock_instance = mock_pricer_class

    agent = FTPriceAgent()

    mock_from_name.assert_called_once_with(APP_NAME, "FTPricer")
    assert agent.ftpricer == mock_instance


def test_price_call(mock_pricer_class):
    """Test the price method calls the remote Modal method correctly."""
    _, mock_instance = mock_pricer_class
    agent = FTPriceAgent()

    description = "A brand new 4K TV with HDR10+ and HDMI 2.1 support"
    price = agent.price(description)

    mock_instance.price.remote.assert_called_once_with(description)
    assert price == 42.0


def test_price_returns_zero_on_exception():
    """Test fallback behavior if remote call fails (e.g., simulate error)."""
    with patch("modal.Cls.from_name") as mock_from_name:
        mock_instance = MagicMock()
        mock_instance.price.remote.side_effect = Exception("Remote failure")
        mock_from_name.return_value = MagicMock(return_value=mock_instance)

        agent = FTPriceAgent()

        with pytest.raises(RuntimeError) as exc_info:
            agent.price("Faulty input")
        assert isinstance(exc_info.value.__cause__, Exception)
        assert "Remote failure" in str(exc_info.value.__cause__)


def test_extract_tagged_price():
    """Test parsing of price strings."""
    assert extract_tagged_price("Price is $49.98") == 49.98
    assert extract_tagged_price("Price is $1,299.99") == 1299.99
    assert extract_tagged_price("Price is $") == 0.0
    assert extract_tagged_price("unexpected format") == 0.0
