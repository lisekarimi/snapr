"""Test module for PlanningAgent."""

from typing import List
from unittest.mock import MagicMock, patch

import pytest

from src.agents.planning_agent import PlanningAgent
from src.deals.structured_deals import Opportunity


@pytest.fixture
def fake_opportunity() -> Opportunity:
    """Returns a mock Opportunity for use in tests."""
    return Opportunity(
        product_description="Sample product",
        price=100.0,
        url="https://example.com/deal",
    )


@patch("src.agents.planning_agent.DealScannerAgent")
@patch("src.agents.planning_agent.EnsemblePriceAgent")
def test_initialization(
    mock_ensemble_cls: MagicMock, mock_scanner_cls: MagicMock
) -> None:
    """Tests that sub-agents are initialized and logs are emitted."""
    with patch.object(PlanningAgent, "log") as mock_log:
        agent = PlanningAgent()

        # Ensure agent dependencies are instantiated
        mock_scanner_cls.assert_called_once()
        mock_ensemble_cls.assert_called_once()
        assert agent.scanner == mock_scanner_cls.return_value
        assert agent.ensemble == mock_ensemble_cls.return_value

        # Ensure logging occurred
        assert mock_log.call_count >= 1


@patch("src.agents.planning_agent.save_opportunities_to_memory")
@patch("src.agents.planning_agent.EnsemblePriceAgent")
@patch("src.agents.planning_agent.DealScannerAgent")
def test_plan_flow(
    mock_scanner_cls: MagicMock,
    mock_ensemble_cls: MagicMock,
    mock_save_memory: MagicMock,
    fake_opportunity: Opportunity,
) -> None:
    """Tests the end-to-end planning flow for one valid opportunity."""
    # Mock scanner with one scraped deal
    mock_scanner = MagicMock()
    mock_scanner.scan.return_value.opportunities = [fake_opportunity]
    mock_scanner_cls.return_value = mock_scanner

    # Mock ensemble to return a higher market price → discount = 80
    mock_ensemble = MagicMock()
    mock_ensemble.price.return_value = 180.0
    mock_ensemble_cls.return_value = mock_ensemble

    agent = PlanningAgent()
    results: List[Opportunity] = agent.plan(categories=["tech", "home"])

    # Check final result and enrichment
    assert len(results) == 1
    enriched = results[0]
    assert enriched.discount == 80.0
    assert enriched.estimate == 180.0

    # Ensure calls were made correctly
    mock_scanner.scan.assert_called_once_with(["tech", "home"])
    mock_ensemble.price.assert_called_once_with(fake_opportunity.product_description)
    mock_save_memory.assert_called_once()
    assert len(mock_save_memory.call_args[0][0]) == 1


@patch("src.agents.planning_agent.DealScannerAgent")
def test_no_deals_found(mock_scanner_cls: MagicMock) -> None:
    """Tests that an empty result is returned when scanner finds nothing."""
    mock_scanner = MagicMock()
    mock_scanner.scan.return_value = None
    mock_scanner_cls.return_value = mock_scanner

    agent = PlanningAgent()
    results: List[Opportunity] = agent.plan(categories=["tech", "home"])
    assert results == []


def test_log_result_accept_reject() -> None:
    """Tests whether accepted and rejected deals are logged correctly."""
    agent = PlanningAgent()

    with patch.object(agent, "log") as mock_log:
        # Deal above threshold
        opp = Opportunity(
            product_description="Test", price=100, url="url", estimate=200, discount=100
        )
        agent._log_result(1, opp)
        mock_log.assert_any_call("✅ Deal #1 accepted — discount: $100.00")

        # Deal below threshold
        opp.discount = 10
        agent._log_result(2, opp)
        mock_log.assert_any_call(
            "❌ Deal #2 rejected — discount below threshold: $10.00"
        )


def test_report_summary_no_deals() -> None:
    """Tests the summary log when no deals meet the threshold."""
    agent = PlanningAgent()

    with patch.object(agent, "log") as mock_log:
        agent._report_summary([])
        mock_log.assert_called_with("❌ No opportunities met the discount threshold.")


def test_report_summary_with_deals(fake_opportunity: Opportunity) -> None:
    """Tests that accepted deals are printed correctly in summary."""
    agent = PlanningAgent()
    fake_opportunity.estimate = 150
    fake_opportunity.discount = 50

    with patch("src.agents.planning_agent.console.print") as mock_print:
        agent._report_summary([fake_opportunity])
        mock_print.assert_called_once()
        assert "Price" in mock_print.call_args[0][0]
