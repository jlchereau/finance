"""
Asset module
"""

import datetime
from enum import Enum
from abc import ABC, abstractmethod
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

from .utils import get_sma


class AssetType(Enum):
    """
    Asset Type
    """
    EQUITY = 0
    ETF = 1


class Asset(ABC):
    """
    Asset class
    """

    def __init__(self, ticker: str):
        """
        Constructor
        """
        self._date = datetime.date.today()
        self._yahoo_ticker = yf.Ticker(ticker)
        self._history = None

    # ----------------------------------------------------------------------------
    # General
    # ----------------------------------------------------------------------------

    @property
    def yahoo_ticker(self) -> yf.Ticker:
        """
        Yahoo Ticker
        """
        return self._yahoo_ticker

    @property
    def symbol(self) -> str:
        """
        Symbol
        """
        return self._yahoo_ticker.info['symbol']

    @property
    def name(self) -> str:
        """
        Name
        """
        return self._yahoo_ticker.info['longName']

    @property
    def type(self) -> AssetType:
        """
        Asset type
        """
        return AssetType[self._yahoo_ticker.info['quoteType']]

    @property
    def currency(self) -> str:
        """
        Currency
        """
        return self._yahoo_ticker.info['currency']

    # ----------------------------------------------------------------------------
    # Market data
    # ----------------------------------------------------------------------------

    @property
    def previous_close(self) -> float:
        """
        Previous close price
        """
        return self._yahoo_ticker.info['previousClose']

    @property
    def volume(self) -> int:
        """
        Volume
        TODO: understand the 5 measures of volume available
        """
        return self._yahoo_ticker.info['volume']

    # ----------------------------------------------------------------------------
    # Balance sheet (only for Equity)
    # ----------------------------------------------------------------------------

    # ----------------------------------------------------------------------------
    # Income statement (only for Equity)
    # ----------------------------------------------------------------------------

    # ----------------------------------------------------------------------------
    # Cash flow statement (only for Equity)
    # ----------------------------------------------------------------------------

    # ----------------------------------------------------------------------------
    # Finance KPIs (only for Equity)
    # ----------------------------------------------------------------------------

    # ----------------------------------------------------------------------------
    # Historical data
    # ----------------------------------------------------------------------------

    def __load_history(
            self,
            period='max'
            ):
        """
        Load historical data
        """
        self._history = self._yahoo_ticker.history(
            period=period, interval='1d', auto_adjust=True)
        # When auto_adjust == True, Close is actually Adj Close
        # as defined by CRSP rules:
        # https://help.yahoo.com/kb/adjusted-close-sln28256.html
        # See also https://github.com/ranaroussi/yfinance/issues/1333
        self._history.index = self._history.index \
            .tz_localize(None).to_period('D')
        self._history['Return'] = self._history[['Close']].pct_change()
        # Drop missing values
        # self._history.dropna(inplace=True)
        # Fill missing values by interpolating with method
        # that takes average of previous and next values
        # self._history.interpolate(method='linear',
        #                           limit_direction='both', inplace=True)

    # ----------------------------------------------------------------------------
    # Statistics
    # ----------------------------------------------------------------------------

    @property
    def rsi_14(self) -> float:
        """
        Relative Strength Index (RSI)
        """
        # pass

    # ----------------------------------------------------------------------------
    # Information report
    # ----------------------------------------------------------------------------

    @property
    @abstractmethod
    def info(self) -> pd.Series:
        """
        Information report
        """
        # pass

    # ----------------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------------

    def plot(self, period: str = 'max', sma: tuple = (50, 200)):
        """
        Plot price and volume history
        """
        self.__load_history(period=period)
        df = self._history[['Close', 'Volume']].dropna()
        x = df.index.astype('datetime64[ns]')
        fig, (ax1, ax2) = plt.subplots(2, height_ratios=(0.7, 0.3))

        # Set title
        fig.suptitle(f'{self.name} ({self.symbol})')
        
        # Plot the price line charts
        ax1.plot(x, df['Close'], label='Close Price')
        for window in sma:
            df[f'SMA_{window}'] = get_sma(df['Close'], window=window)
            ax1.plot(x, df[f'SMA_{window}'], label=f'SMA_{window}')
        ax1.set_ylabel('Close Price')
        # ax1.tick_params(axis='y', labelcolor='blue')

        # Create the 'Volume' bar chart
        ax2.bar(x, df['Volume'], color='red', label='Volume')
        ax2.set_ylabel('Volume')
        # ax2.tick_params(axis='y', labelcolor='gray')

        # Show plot
        plt.show()
