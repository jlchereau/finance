"""
Test utils
"""

import random
import pytest
import pandas as pd
import yfinance as yf

# get_ema, get_rsi, get_macd, get_bollinger_bands, \
from src.folib.utils import get_sma, get_cagr, \
    get_avg_pct_change, get_linear_forecast, \
    get_next_pct_change_from_regression


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


# @pytest.mark.parametrize("input, output",
# [(5.234, 5), (9.99, 10), (0.456, 0), (7.905, 7)])
def test_get_cagr():
    """
    Test get_cagr
    """
    data = pd.Series(data=[100, 110, 121],
                     index=['2022-01-01', '2023-01-01', '2024-01-01'])
    assert pytest.approx(get_cagr(data)) == 0.1


def test_get_avg_pct_change():
    """
    Test get_avg_pct_change
    """
    data = pd.Series(data=[100, 110, 132],
                     index=['2022-01-01', '2023-01-01', '2024-01-01'])
    assert pytest.approx(get_avg_pct_change(data)) == 0.15


def test_get_linear_forecast():
    """
    Test get_linear_forecast
    """
    data = pd.Series(data=[100, 110, 120],
                     index=['2022-01-01', '2023-01-01', '2024-01-01'])
    assert pytest.approx(get_linear_forecast(data, 1).iloc[0]) == 130


def test_get_next_pct_change_from_regression():
    """
    Test get_next_pct_change_from_regression
    """
    data = pd.Series(data=[100, 110, 132],
                     index=['2022-01-01', '2023-01-01', '2024-01-01'])
    assert pytest.approx(get_next_pct_change_from_regression(data)) == 0.3
