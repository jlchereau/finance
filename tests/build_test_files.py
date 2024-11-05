"""
Build a test file to cache data from Yahoo Finance API
to avoid hitting the rate limit
"""

import yfinance as yf

T = 'KO'  # Coca-Cola has a long history
yt = yf.Ticker(T)
data = yt.history(period='max', interval='1d', auto_adjust=True)
data.to_csv('quote.csv')
