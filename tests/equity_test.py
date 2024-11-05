"""
Unit tests for Asset class
"""

import random
import pandas as pd
import yfinance as yf

from src.folib.utils import AssetType
from src.folib.equity import Equity as Asset

TICKERS = [
    'AAPL',     # US stock
    'COUR',     # US stock
    'BYDDY',    # US ADR
    'TSM',      # US ADR
    'ASML.AS',  # NL stock
    'TTE.PA',   # FR stock
    ]
T = random.choice(TICKERS)
print(f'Ticker {T}')


def test_yahoo_ticker():
    """
    test that yahoo_ticker is a yfinance Ticker object
    TODO test bad yahoo ticker
    """
    asset = Asset(T)
    assert isinstance(asset.yahoo_ticker, yf.Ticker)


# ----------------------------------------------------------------------------
# General
# ----------------------------------------------------------------------------


def test_symbol():
    """
    test that symbol is the actual ticker used to initialize the object
    """
    asset = Asset(T)
    assert asset.symbol == T


def test_name():
    """
    test that name is a non empty string
    """
    asset = Asset(T)
    assert isinstance(asset.name, str)
    assert len(asset.name) > 0


def test_type():
    """
    test that type is a non empty string
    """
    asset = Asset(T)
    assert isinstance(asset.type, AssetType)


def test_industry():
    """
    test that industry is a non empty string
    """
    asset = Asset(T)
    assert isinstance(asset.industry, str)
    assert len(asset.industry) > 0


def test_sector():
    """
    test that sector is a non empty string
    """
    asset = Asset(T)
    assert isinstance(asset.sector, str)
    assert len(asset.sector) > 0


# TODO morningstar moat


def test_currency():
    """
    test that currency is 3-char string
    """
    asset = Asset(T)
    assert isinstance(asset.currency, str)
    assert len(asset.currency) == 3


def test_financial_currency():
    """
    test that financial currecny is a 3-char string or None
    """
    asset = Asset(T)
    assert isinstance(asset.financial_currency, str)
    assert len(asset.financial_currency) == 3


# ----------------------------------------------------------------------------
# Market data
# ----------------------------------------------------------------------------


def test_previous_close():
    """
    test that previous close is a positive number
    """
    asset = Asset(T)
    assert isinstance(asset.previous_close, float)
    assert asset.previous_close > 0


def test_shares_outstanding():
    """
    test that shares outstanding is a positive integer
    """
    asset = Asset(T)
    assert isinstance(asset.shares_outstanding, int)
    assert asset.shares_outstanding > 0


def test_market_cap():
    """
    test that market cap is a positive number
    """
    asset = Asset(T)
    assert isinstance(asset.market_cap, float)
    assert asset.market_cap > 0


def test_beta():
    """
    test that beta is a positive number or None
    """
    asset = Asset(T)
    if asset.beta is not None:
        assert isinstance(asset.beta, float)
        assert asset.beta > 0


# ----------------------------------------------------------------------------
# Balance sheet
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Income statement
# ----------------------------------------------------------------------------


def test_annual_revenue():
    """
    test that annual revenue is a pd.Series
    """
    asset = Asset(T)
    assert isinstance(asset.annual_revenue, pd.Series)


def test_revenue_cagr():
    """
    test that revenue cagr is a float
    """
    asset = Asset(T)
    assert isinstance(asset.revenue_cagr, float)


def test_annual_gross_profit():
    """
    test that annual gross profit is a pd.Series
    """
    asset = Asset(T)
    assert isinstance(asset.annual_gross_profit, pd.Series)


def test_gross_margin_avg():
    """
    test that growth profit avg is a float
    """
    asset = Asset(T)
    assert isinstance(asset.gross_margin_avg, float)


def test_annual_selling_general_and_admin():
    """
    test that annual selling general and admin is a pd.Series
    """
    asset = Asset(T)
    assert isinstance(asset.annual_selling_general_and_admin, pd.Series)


def test_annual_research_and_development():
    """
    test that annual reasearch and development is a pd.Series
    """
    asset = Asset(T)
    assert isinstance(asset.annual_research_and_development, pd.Series)

# ----------------------------------------------------------------------------
# Cash flow statement
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Finance KPIs
# ----------------------------------------------------------------------------


def test_trailing_pe():
    """
    test that trailing P/E is a positive number or None
    """
    asset = Asset(T)
    if asset.type == AssetType.EQUITY:
        assert isinstance(asset.trailing_pe, float)
        assert asset.trailing_pe > 0
    elif asset.type == AssetType.ETF:
        assert asset.trailing_pe is None


def test_forward_pe():
    """
    test that forward P/E is a positive number or None
    """
    asset = Asset(T)
    if asset.type == AssetType.EQUITY:
        assert isinstance(asset.forward_pe, float)
        assert asset.forward_pe > 0
    elif asset.type == AssetType.ETF:
        assert asset.forward_pe is None


# ----------------------------------------------------------------------------
# Information report
# ----------------------------------------------------------------------------


def test_info():
    """
    test short information report
    """
    asset = Asset(T)
    assert isinstance(asset.info, pd.Series)


# ----------------------------------------------------------------------------
# Plots
# ----------------------------------------------------------------------------
