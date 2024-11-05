"""Unit tests for Asset class"""

import random
import pandas as pd
import yfinance as yf

from src.folib.utils import AssetType
from src.folib.etf import ETF as Asset

TICKERS = [
    'SPY',      # US stock ETF
    'AGG',      # US bond ETF
    'IWLE.DE'   # DE stock ETF
    'IEAA.L'    # L bond ETF
    ]
T = random.choice(TICKERS)
print(f'Ticker {T}')


def test_yahoo_ticker():
    """
    test that yahoo_ticker is a yfinance Ticker object
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


def test_currency():
    """
    test that currency is 3-char string
    """
    asset = Asset(T)
    assert isinstance(asset.currency, str)
    assert len(asset.currency) == 3


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


def test_total_assets():
    """
    test that total assets is a positive number
    """
    asset = Asset(T)
    if asset.total_assets is not None:
        assert isinstance(asset.total_assets, int)
        assert asset.total_assets > 0


# ----------------------------------------------------------------------------
# FinanciaBlancels
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# KPIs
# ----------------------------------------------------------------------------


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
