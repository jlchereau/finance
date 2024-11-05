"""
Equity module
"""

import pandas as pd

from .utils import AssetType, get_cagr
from .asset import Asset


class Equity(Asset):
    """
    Equity class
    """

    def __init__(self, ticker: str):
        """
        Constructor
        """
        super().__init__(ticker)
        assert self.type == AssetType.EQUITY, f'{ticker} is not an equity!'

    # ----------------------------------------------------------------------------
    # General
    # ----------------------------------------------------------------------------

    @property
    def industry(self) -> str | None:
        """
        Industry
        """
        return self._yahoo_ticker.info['industry']

    @property
    def sector(self) -> str | None:
        """
        Sector (Sector is broader than Industry)
        """
        return self._yahoo_ticker.info['sector']

    @property
    def financial_currency(self) -> str | None:
        """
        Financial currency (especially for ADRs)
        """
        return self._yahoo_ticker.info['financialCurrency']

    # ----------------------------------------------------------------------------
    # Market data
    # ----------------------------------------------------------------------------

    @property
    def shares_outstanding(self) -> float | None:
        """
        Number of shares outstanding
        """
        return self._yahoo_ticker.info['sharesOutstanding']

    @property
    def market_cap(self) -> float | None:
        """
        Market capitalization
        """
        # Yahoo's 'marketCap' is based on 'currentPrice',
        # base it on 'previousClose'
        # return self._yahoo_ticker.info['marketCap']
        return self.shares_outstanding * self.previous_close

    @property
    def trailing_eps(self) -> float | None:
        """
        Trailing EPS
        """
        if 'trailingEPS' in self._yahoo_ticker.info:
            return self._yahoo_ticker.info['trailingEPS']
        return None

    @property
    def forward_eps(self) -> float | None:
        """
        Forward P/E ratio
        """
        if 'forwardEPS' in self._yahoo_ticker.info:
            return self._yahoo_ticker.info['forwardEPS']
        return None

    @property
    def trailing_pe(self) -> float | None:
        """
        Trailing P/E ratio
        """
        if 'trailingPE' in self._yahoo_ticker.info:
            return self._yahoo_ticker.info['trailingPE']
        return None

    @property
    def forward_pe(self) -> float | None:
        """
        Forward P/E ratio
        """
        if 'forwardPE' in self._yahoo_ticker.info:
            return self._yahoo_ticker.info['forwardPE']
        return None

    @property
    def beta(self) -> float | None:
        """
        Beta
        """
        if 'beta' in self._yahoo_ticker.info:
            return self._yahoo_ticker.info['beta']
        return None

    # ----------------------------------------------------------------------------
    # Balance sheet
    # - https://www.youtube.com/watch?v=As1a2VgbdWg
    # - https://www.youtube.com/watch?v=Uuy4xYJoh0w
    #
    # 1) Cash & Equivalents / Debt > 1 (quick ratio) indicates a company that
    # has more cash than debts
    # 2) Total Liabilities / Shareholder's Equity < 0.8 (debt-to-equity ratio)
    # indicates low debt and financial stability
    # 3) No preferred stock to avoid risk of dilution and complex valuation
    # (impact on DCF analysis)
    # 4) Retained Earnings Growth (Yn+1 / Yn-1) demonstrates consistent
    # profitability and recession-proof growth
    # 5) Treasury stocks indicate shares buybacks which increase shareholder
    # value, and...
    # 6) Return on Equity > 0.15 indicates how efficiently a company uses
    # its equity to generate profits.
    # ----------------------------------------------------------------------------

    @property
    def quick_ratio(self) -> float:
        """
        Quick ratio
        """
        return self._yahoo_ticker.info['quickRatio']

    @property
    def debt_to_equity(self) -> float:
        """
        Debt to Equity
        """
        if 'debtToEquity' in self._yahoo_ticker.info:
            return self._yahoo_ticker.info['debtToEquity']
        return None

    # preferred stock

    # retained earnings

    # treasury stock

    @property
    def return_on_equity(self) -> float:
        """
        Return on Equity
        """
        if 'returnOnEquity' in self._yahoo_ticker.info:
            return self._yahoo_ticker.info['returnOnEquity']
        return None

    # ----------------------------------------------------------------------------
    # Income statement
    # - https://www.youtube.com/watch?v=oTsnwBqq7S0
    # - https://www.youtube.com/watch?v=uFzIsJwAjfk
    #
    # 1) Gross Margin > 0.4 indicates operational efficiency and pricing power.
    # 2) SG&A / Gross Profit < 0.3 indicates products that sell themselves.
    # 3) R&D / Gross Profit < 0.3 indicates a simple business.
    # 4) Interest Expense / Operating Income < 0.15
    # indicates a low cost of debt.
    # 5) Income Tax / Pre-tax Income ~= 0.2 indicates no scheme
    # 6) Net income / Revenue > 0.2 indicates a profitable business
    # 7) Earnings Per Share growing regularly
    # compound investors’ returns over time
    # ----------------------------------------------------------------------------

    @property
    def annual_revenue(self) -> pd.Series:
        """
        Annual revenue
        """
        # Improve with analyst forecasts
        # Cnnsider operating revenue rather than total revenue
        return self._yahoo_ticker.income_stmt \
            .loc['Total Revenue'].sort_index().dropna()

    @property
    def revenue_cagr(self) -> float:
        """
        Revenue cagr
        """
        # Consider mixing with quarterly revenues for recent data
        return get_cagr(self.annual_revenue)

    @property
    def annual_gross_profit(self) -> pd.Series:
        """
        Annual gross Profit
        """
        return self._yahoo_ticker.income_stmt \
            .loc['Gross Profit'].sort_index().dropna()

    @property
    def gross_margin_avg(self) -> float:
        """
        Gross Margin average
        """
        return (self.annual_gross_profit / self.annual_revenue).mean()

    @property
    def annual_selling_general_and_admin(self) -> pd.Series:
        """
        Selling General And Administration
        """
        # Improve with analyst forecasts
        return self._yahoo_ticker.income_stmt \
            .loc['Selling General And Administration'] \
            .sort_index().dropna()

    @property
    def selling_general_and_admin_ratio(self) -> float:
        """
        Selling General And Administration ratio
        """
        return (self.annual_selling_general_and_admin
                / self.annual_gross_profit).mean()

    @property
    def annual_research_and_development(self) -> pd.Series:
        """
        Research And Development
        """
        return self._yahoo_ticker.income_stmt \
            .loc['Research And Development'] \
            .sort_index().dropna()

    @property
    def research_and_development_ratio(self) -> float:
        """
        Research And Development ratio
        """
        return (self.annual_research_and_development
                / self.annual_gross_profit).mean()

    # ----------------------------------------------------------------------------
    # Cash flow statement
    # ----------------------------------------------------------------------------

    def intrinsic_value(self) -> float:
        """
        Intrinsic value
        """
        # pass

    # ----------------------------------------------------------------------------
    # Analyst data
    # ----------------------------------------------------------------------------

    def analyst_recommendation(self) -> str:
        """
        Analyst recommendation
        """
        return self._yahoo_ticker.recommendations \
            .sort_index().dropna().iloc[-1]['To Grade']

    # ----------------------------------------------------------------------------
    # Statistics
    # ----------------------------------------------------------------------------

    # ----------------------------------------------------------------------------
    # Information report
    # ----------------------------------------------------------------------------

    @property
    def info(self):
        """Show an asset report"""
        return pd.Series({
            'date': self._date,
            # -------- General
            'symbol': self.symbol,
            'name': self.name,
            'type': self.type.name,
            'industry': self.industry,
            'sector': self.sector,
            'currency': self.currency,
            'financial_currency': self.financial_currency,
            # -------- Market data
            'shares_outstanding': self.shares_outstanding,
            'market_cap': self.market_cap,
            'previous_close': self.previous_close,
            'trailing_eps': self.trailing_eps,
            'forward_eps': self.forward_eps,
            'trailing_pe': self.trailing_pe,
            'forward_pe': self.forward_pe,            
            'beta': self.beta,
            # -------- Balance sheet
            'quick_ratio': self.quick_ratio,
            'debt_to_equity': self.debt_to_equity,
            'return_on_equity': self.return_on_equity,
            # -------- Income statement
            'revenue_cagr': self.revenue_cagr,
            # 'gross_margin_avg': self.gross_margin_avg,
            # 'selling_general_and_admin_ratio':
            #   self.selling_general_and_admin_ratio,
            # 'research_and_development_ratio':
            #   self.research_and_development_ratio,
            # -------- Cash flow statement
            # intrinsic_value
            # -------- Statistics
            'rsi_14': super().rsi_14,
            })
