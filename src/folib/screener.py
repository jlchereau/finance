"""
Screener module
"""

import functools
import pandas as pd
from tqdm.auto import tqdm
from .equity import Equity


GROWTH_EQUITY_FILTER = {
    'forward_pe': lambda x: isinstance(x, float) and x > 0 and x <= 20,
    'quick_ratio': lambda x: isinstance(x, float) and x >= 1 and x <= 2,
    'debt_to_equity': lambda x: isinstance(x, float) and x >= 0.5 and x <= 1,
    'return_on_equity': lambda x: isinstance(x, float) and x >= 0.15,
    'revenue_growth': lambda x: isinstance(x, float) and x >= 0.1,
    'delta_intrinsic_value': lambda x: isinstance(x, float) and x > 0.2,
    'delta_graham_value': lambda x: isinstance(x, float) and x > 0.2
}


class ScreenerFilter():
    """
    Screener filter class
    TODO Consider scoring each equity intead of filtering
    """

    def __init__(self, filter_dict: dict | None = None):
        """
        Constructor
        """
        if filter_dict is None:
            filter_dict = {}
        self._filter_dict = filter_dict

    def filter(self, equity: Equity) -> bool:
        """
        Filter equity
        """
        ret = True
        for key, filter_func in self._filter_dict.items():
            if key in equity.info and callable(filter_func):
                ret = filter_func(equity.info[key])
                if not ret:
                    break
        return ret

    def prettify(self, data: pd.DataFrame):
        """
        Prettify data
        """
        def build_styler(styler):
            for key, filter_func in self._filter_dict.items():
                if key in data.columns and callable(filter_func):
                    def highlight(val, filter_func):
                        # https://pylint.readthedocs.io/en/latest/user_guide/messages/warning/cell-var-from-loop.html
                        return 'color: white; background-color: green' \
                            if filter_func(val) else ''
                    # Bind `filter_func`
                    # to the specific instance of `highlight`
                    highlight_partial = \
                        functools.partial(highlight, filter_func=filter_func)
                    styler = styler.map(highlight_partial, subset=[key])
            return styler
        return data.style.pipe(build_styler)


class Screener():
    """
    Screener class
    TODO Consider multithreading
    TODO Consider scoring
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

    def to_dataframe(self,
                     screener_filter: ScreenerFilter = ScreenerFilter(),
                     show_all: bool = False):
        """
        Get equities as a dataframe (using info)
        """
        columns = self._equities[0].info.to_frame().T.columns
        df = pd.DataFrame(columns=columns)
        for equity in tqdm(self._equities):
            try:
                if show_all or screener_filter.filter(equity):
                    df = pd.concat([df, equity.info.to_frame().T],
                                   ignore_index=True)
            except Exception as e:  # pylint: disable=W0718
                print(f'Error filtering {equity.symbol}: {e}')
        df.drop(columns=['date', 'type'], inplace=True)
        df.set_index('symbol', inplace=True)
        return screener_filter.prettify(df)
