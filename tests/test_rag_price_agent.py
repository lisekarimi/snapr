"""Test module for RAGPriceAgent."""

from unittest.mock import MagicMock, call, patch

import pytest

from src.agents.rag_price_agent import RAGPriceAgent
from src.modal_services.app_config import APP_NAME
from src.utils.text_utils import extract_price


@pytest.fixture
def mock_modal():
    """Mocks Modal remote class."""
    with patch("modal.Cls.from_name") as mock_from_name:
        mock_remote_instance = MagicMock()
        mock_remote_cls = MagicMock(return_value=mock_remote_instance)
        mock_from_name.return_value = mock_remote_cls
        yield mock_from_name, mock_remote_instance


@pytest.fixture
def agent(mock_modal):
    """Returns an agent with mocked remote."""
    with patch.object(RAGPriceAgent, "log") as mock_log:
        agent = RAGPriceAgent()
        yield agent, mock_log


def test_initialization(agent, mock_modal):
    """Tests the agent initialization process."""
    agent_instance, mock_log = agent
    mock_from_name, _ = mock_modal

    # Ensure the RAG component was initialized
    assert agent_instance.rag is not None

    # Check that the correct remote class was loaded via Modal
    mock_from_name.assert_called_once_with(APP_NAME, "RAGPricer")

    # Confirm that a log message was emitted during initialization
    mock_log.assert_called()


def test_price_success(agent):
    """Tests successful price prediction flow."""
    agent_instance, mock_log = agent

    # Mock remote call
    expected_price = 99.95
    agent_instance.rag.price.remote = MagicMock(return_value=expected_price)

    # Test the price method
    result = agent_instance.price("Gaming laptop with RTX 4080")

    # Verify the result and interactions
    assert result == expected_price
    agent_instance.rag.price.remote.assert_called_once_with(
        "Gaming laptop with RTX 4080"
    )


def test_price_extraction_logic(agent):
    """Tests that the price extraction via regex works correctly.

    Verifies that the function returns a float rounded to 2 decimals.
    """
    agent_instance, mock_log = agent

    # Mock rag.price.remote to simulate various GPT outputs
    test_cases = [
        ("$42.00", 42.00),
        ("42 dollars", 42.00),
        ("$1234.5678", 1234.57),
        ("Price is $0.99", 0.99),
        ("Ninety nine", 0.0),  # Invalid text should fallback to 0
        ("$1,234.56", 1234.56),
        ("about 50", 50.00),
    ]

    for reply, expected_price in test_cases:
        price = extract_price(reply)

        assert isinstance(price, float)
        assert price == expected_price


def test_price_remote_exception():
    """Tests error handling when Modal remote call fails."""
    # Create fresh mocks for this test
    with patch("modal.Cls.from_name") as mock_from_name:
        # Setup the mock to raise an exception on remote call
        mock_remote_instance = MagicMock()
        mock_remote_instance.price.remote.side_effect = Exception(
            "Modal connection failed"
        )
        mock_remote_cls = MagicMock(return_value=mock_remote_instance)
        mock_from_name.return_value = mock_remote_cls

        # Mock the log method
        with patch.object(RAGPriceAgent, "log") as mock_log:
            agent = RAGPriceAgent()

            # Test exception handling
            with pytest.raises(RuntimeError) as excinfo:
                agent.price("Product that causes error")

            # Verify exception details
            assert "RAGPriceAgent failed to get price from Modal" in str(excinfo.value)

            # Verify error was logged
            mock_log.assert_any_call(
                "[ERROR] Remote RAGPricer failed: Modal connection failed"
            )


def test_agent_with_modal_import_error():
    """Tests handling of Modal import errors."""
    with patch("modal.Cls.from_name", side_effect=ImportError("Modal not installed")):
        with patch.object(RAGPriceAgent, "log") as mock_log:
            with pytest.raises(ImportError):
                RAGPriceAgent()

            # Ensure no logs are called since init fails before log
            mock_log.assert_not_called()


def test_multiple_price_calls(agent):
    """Tests that multiple price calls work correctly."""
    agent_instance, mock_log = agent

    # Setup mock to return different values on successive calls
    agent_instance.rag.price.remote = MagicMock(side_effect=[10.50, 25.99, 199.95])

    # Make multiple calls
    results = []
    descriptions = ["Small item", "Medium item", "Premium item"]

    for desc in descriptions:
        mock_log.reset_mock()
        result = agent_instance.price(desc)
        results.append(result)

    # Verify results
    assert results == [10.50, 25.99, 199.95]

    # Verify all calls were made correctly
    expected_calls = [call(desc) for desc in descriptions]
    assert agent_instance.rag.price.remote.call_args_list == expected_calls
