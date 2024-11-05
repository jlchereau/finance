"""
Portfolio module
"""

import yfinance as yf


class Portfolio():
    """
    Portfolio class
    """

    def __init__(self, tickers: list, weights: list):
        """
        Constructor
        """
        self._tickers = tickers
        self._yahoo_tickers = yf.Tickers(tickers)
        self._weights = weights
        self.__load_history()

    def __load_history(self, period: str = 'max'):
        """
        Load history
        """
        df = self._yahoo_tickers.history(period=period, interval='1d',
                                         auto_adjust=True)
        df.index = df.index.tz_convert(None).to_period('D')
        df = df.astype(float).pct_change()
