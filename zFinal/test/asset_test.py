import random
import yfinance as yf
from ..folib.asset import Asset

TICKERS = ["AAPL", "AMZN", "MSFT", "GOOG", "TSLA"]
T = random.choice(TICKERS)
print(f"Ticker {T}")

# test yahoo_ticker
def test_yahoo_ticker():
    asset = Asset(T)
    assert isinstance(asset.yahoo_ticker, yf.Ticker)

# test symbol
def test_symbol():
    asset = Asset(T)
    assert asset.symbol == T