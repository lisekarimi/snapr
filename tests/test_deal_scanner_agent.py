"""Test module for DealScannerAgent."""

from typing import List
from unittest.mock import MagicMock, patch

import pytest

from src.agents.deal_scanner_agent import DealScannerAgent
from src.deals.raw_deals import ScrapedDeal
from src.deals.structured_deals import OpportunitiesCollection, Opportunity
from src.models.frontier_model import OPENAI_MODEL

TEST_CATEGORIES = ["tech", "home"]


@pytest.fixture
def agent() -> DealScannerAgent:
    """Fixture to create a test instance of DealScannerAgent."""
    return DealScannerAgent()


@pytest.fixture
def sample_scraped_deals() -> List[MagicMock]:
    """Fixture to create mock sample deals for testing."""
    deals = [
        MagicMock(spec=ScrapedDeal, url="https://example.com/deal1"),
        MagicMock(spec=ScrapedDeal, url="https://example.com/deal2"),
        MagicMock(spec=ScrapedDeal, url="https://example.com/deal3"),
    ]

    # Configure the mock objects to return specific values when describe() is called
    for i, deal in enumerate(deals):
        deal.describe.return_value = (
            f"Title: Sample Deal {i + 1}\n"
            f"Details: This is deal {i + 1}\n"
            f"Features: Feature A, Feature B\n"
            f"URL: {deal.url}"
        )
    return deals


@pytest.fixture
def memory_entries() -> List[MagicMock]:
    """Fixture for sample memory entries (already processed deals)."""
    return [
        MagicMock(deal=MagicMock(url="https://example.com/old_deal1")),
        MagicMock(deal=MagicMock(url="https://example.com/old_deal2")),
        MagicMock(deal=MagicMock(url="https://example.com/deal3")),
    ]


@pytest.fixture
def mock_api_response() -> MagicMock:
    """Fixture for sample API response structure."""
    response = MagicMock()
    response.choices = [
        MagicMock(
            message=MagicMock(
                parsed=OpportunitiesCollection(
                    opportunities=[
                        Opportunity(
                            product_description="Product 1 description",
                            price=99.99,
                            url="https://example.com/deal1",
                        ),
                        Opportunity(
                            product_description="Product 2 description",
                            price=149.99,
                            url="https://example.com/deal2",
                        ),
                        Opportunity(
                            product_description="Product 3 description",
                            price=0,
                            url="https://example.com/deal3",
                        ),  # Invalid price
                        Opportunity(
                            product_description="Product 4 description",
                            price=199.99,
                            url="https://example.com/deal4",
                        ),
                        Opportunity(
                            product_description="Product 5 description",
                            price=49.99,
                            url="https://example.com/deal5",
                        ),
                    ]
                )
            )
        )
    ]
    return response


@patch("src.deals.raw_deals.ScrapedDeal.fetch")
@patch.object(DealScannerAgent, "_load_memory")
def test_fetch_deals(
    mock_load_memory: MagicMock,
    mock_fetch: MagicMock,
    agent: DealScannerAgent,
    sample_scraped_deals: List[ScrapedDeal],
    memory_entries: List[MagicMock],
) -> None:
    """Test fetching deals and filtering out already seen deals."""
    seen_urls = [entry.deal.url for entry in memory_entries]
    mock_load_memory.return_value = {"seen_urls": seen_urls, "memory": []}

    # Add a deal that should be filtered out (already seen)
    seen_deal = MagicMock(spec=ScrapedDeal, url=seen_urls[0])
    mock_fetch.return_value = sample_scraped_deals + [seen_deal]  # total = 4

    # Run the method
    result = agent.fetch_deals(categories=TEST_CATEGORIES)

    # Check that fetch was called
    mock_fetch.assert_called_once()

    # Make sure no result has a URL that's in memory
    for deal in result:
        assert deal.url not in seen_urls

    # Calculate expected (filtered) count
    expected = [deal for deal in mock_fetch.return_value if deal.url not in seen_urls]
    assert len(result) == len(expected)

    # Verify all returned deals are not in memory
    for deal in result:
        assert deal.url not in [entry.deal.url for entry in memory_entries]


def test_make_user_prompt(
    agent: DealScannerAgent, sample_scraped_deals: List[ScrapedDeal]
) -> None:
    """Test building the user prompt for OpenAI with the scraped deals."""
    # Call the method under test
    prompt = agent.make_user_prompt(sample_scraped_deals)

    # Verify the prompt has the expected format
    assert prompt.startswith(
        "Select the 5 best deals with the clearest product descriptions"
    )

    # Verify each deal's description is included in the prompt
    for deal in sample_scraped_deals:
        assert deal.describe() in prompt


@patch("src.agents.deal_scanner_agent.openai")
@patch("src.agents.deal_scanner_agent.DealScannerAgent.fetch_deals")
def test_scan_with_deals(
    mock_fetch_deals: MagicMock,
    mock_openai: MagicMock,
    sample_scraped_deals: List[ScrapedDeal],
    mock_api_response: MagicMock,
) -> None:
    """Test scanning for deals when new deals are available."""
    # Recreate agent after patching
    agent = DealScannerAgent()

    # Set up mock structure
    mock_openai.beta = MagicMock()
    mock_openai.beta.chat = MagicMock()
    mock_openai.beta.chat.completions = MagicMock()
    mock_openai.beta.chat.completions.parse = MagicMock(return_value=mock_api_response)

    mock_fetch_deals.return_value = sample_scraped_deals

    result = agent.scan(categories=TEST_CATEGORIES)

    mock_fetch_deals.assert_called_once_with(TEST_CATEGORIES)
    mock_openai.beta.chat.completions.parse.assert_called_once()

    call_args = mock_openai.beta.chat.completions.parse.call_args
    assert call_args[1]["model"] == OPENAI_MODEL
    assert len(call_args[1]["messages"]) == 2
    assert call_args[1]["messages"][0]["role"] == "system"
    assert call_args[1]["messages"][1]["role"] == "user"

    # Verify deals with invalid prices were filtered out
    assert len(result.opportunities) == 4  # 5 deals - 1 invalid price
    for opportunity in result.opportunities:
        assert opportunity.price > 0


@patch("src.agents.deal_scanner_agent.DealScannerAgent.fetch_deals")
def test_scan_no_new_deals(
    mock_fetch_deals: MagicMock,
    agent: DealScannerAgent,
) -> None:
    """Test scanning when no new deals are available."""
    # Configure mock to return empty list
    mock_fetch_deals.return_value = []

    # Call the method under test
    result = agent.scan(categories=TEST_CATEGORIES)

    # Verify result is None when no new deals are found
    assert result is None


@pytest.fixture
def mock_openai():
    """Create a mock for the OpenAI client."""
    with patch("src.models.frontier_model.openai") as mock:
        yield mock


@patch("src.agents.deal_scanner_agent.openai")
def test_initialization(mock_openai):
    """Test that the DealScannerAgent initializes correctly and uses openai."""
    with patch.object(DealScannerAgent, "log") as mock_log:
        agent = DealScannerAgent()

        # Confirm OpenAI client is attached
        assert agent.openai == mock_openai

        # Confirm that a log message was emitted
        mock_log.assert_called()


@patch("src.agents.deal_scanner_agent.openai")
@patch("src.agents.deal_scanner_agent.DealScannerAgent.fetch_deals")
def test_scan_openai_failure(
    mock_fetch_deals: MagicMock,
    mock_openai: MagicMock,
    sample_scraped_deals: List[ScrapedDeal],
) -> None:
    """Ensure scan() raises an error when OpenAI call fails."""
    agent = DealScannerAgent()

    # Set up mocks
    mock_fetch_deals.return_value = sample_scraped_deals
    mock_openai.beta = MagicMock()
    mock_openai.beta.chat = MagicMock()
    mock_openai.beta.chat.completions = MagicMock()
    mock_openai.beta.chat.completions.parse.side_effect = Exception("API is down")

    with pytest.raises(
        RuntimeError, match="DealScannerAgent failed to get response from OpenAI"
    ):
        result = agent.scan(categories=TEST_CATEGORIES)
        assert result is None
