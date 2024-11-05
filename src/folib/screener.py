"""
Screener module
"""

import pandas as pd
from tqdm.auto import tqdm
from .equity import Equity


class Screener():
    """
    Screener class
    """

    def __init__(self, tickers: list):
        """
        Constructor
        """
        self._tickers = tickers
        self._equities = []
        self.__load_equities()

    def __load_equities(self):
        """
        Load equities
        """
        self._equities.clear()
        for ticker in tqdm(self._tickers):
            self._equities.append(Equity(ticker))

    @property
    def equities(self):
        """Get equities"""
        return self._equities

    def to_dataframe(self, filter_func: callable = lambda info: True):
        """
        Get equities as a dataframe (using info)
        """
        columns = self._equities[0].info.to_frame().T.columns
        df = pd.DataFrame(columns=columns)
        for equity in tqdm(self._equities):
            try:
                if filter_func(equity.info):
                    df = pd.concat([df, equity.info.to_frame().T],
                                   ignore_index=True)
            except Exception as e:  # pylint: disable=W0718
                print(f'Error processing {equity.symbol}: {e}')
        df.drop(columns=['date', 'type'], inplace=True)
        df.set_index('symbol', inplace=True)
        return df
