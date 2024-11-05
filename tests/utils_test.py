"""
Test utils
"""

import random
import pytest
import pandas as pd
import yfinance as yf

# get_ema, get_rsi, get_macd, get_bollinger_bands, \
from src.folib.utils import get_sma, \
    get_cagr, get_weighted_average_cost_of_capital


TICKERS = [
    'AAPL',     # US stock
    'COUR'
    'BYDDY',    # US ADR
    'TSM',
    'TTE.PA',   # FR stock
    'ASML.AS'   # NL stock
    ]
T = random.choice(TICKERS)
print(f'Ticker {T}')
yt = yf.Ticker(T)
df = yt.history(period='5y', interval='1d', auto_adjust=True)


def test_get_sma():
    """
    Test get_sma

    TODO use talib to check correctness
    """
    sma = get_sma(df['Close'], 50)
    assert isinstance(sma, pd.Series)


def test_get_cagr():
    """Test cagr"""
    data = pd.Series(data=[100, 110], index=['2023-01-01', '2024-01-01'])
    assert pytest.approx(get_cagr(data)) == 0.1


def test_weighted_average_cost_of_capital():
    """Test weighted_average_cost_of_capital"""
    assert isinstance(get_weighted_average_cost_of_capital(yt), float)
