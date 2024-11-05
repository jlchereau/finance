
"""
Test market
"""

import random
# import pytest

from src.folib.market import get_sp500_tickers, \
    get_nasdaq100_tickers, get_msci_world_tickers, \
    get_risk_free_rate, get_market_risk_premium


def test_get_sp500_tickers():
    """
    Test get_sp500_tickers function
    """
    tickers = get_sp500_tickers()
    assert isinstance(tickers, list)
    assert len(tickers) > 500
    assert isinstance(random.choice(tickers), str)


def test_get_nasdaq100_tickers():
    """
    Test get_nasdaq100_tickers function
    """
    tickers = get_nasdaq100_tickers()
    assert isinstance(tickers, list)
    assert len(tickers) > 100
    assert isinstance(random.choice(tickers), str)


def test_get_msci_world_tickers():
    """
    Test get_msci_world_tickers function
    """
    tickers = get_msci_world_tickers()
    assert isinstance(tickers, list)
    assert len(tickers) > 1400
    assert isinstance(random.choice(tickers), str)


def test_get_risk_free_rate():
    """
    Test get_risk_free_rate
    """
    assert get_risk_free_rate() == 0.03


def test_get_market_risk_premium():
    """
    Test get_market_risk_premium
    """
    assert get_market_risk_premium() == 0.05
