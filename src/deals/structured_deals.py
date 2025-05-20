"""Defines post-GPT deal classes.

Used for further analysis as structured opportunities.
"""

from typing import List, Optional

from pydantic import BaseModel


class Opportunity(BaseModel):
    """A single opportunity (final deal) after GPT response."""

    product_description: str  # Full description of the product
    price: float  # Listed price from the deal feed
    url: str  # Link to the product
    estimate: Optional[float] = None  # predicted price
    discount: Optional[float] = None  # estimate - price


class OpportunitiesCollection(BaseModel):
    """A list of top opportunities selected by GPT."""

    opportunities: List[Opportunity]  # High-quality final deals
