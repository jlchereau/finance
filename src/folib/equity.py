"""
Equity module
"""

import pandas as pd

from .asset import Asset, AssetType
from .market import get_risk_free_rate, get_market_risk_premium
from .utils import get_cagr, get_avg_pct_change, \
    get_linear_forecast, get_intrinsinc_value


class Equity(Asset):  # pylint: disable=R0904
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
        if 'trailingEps' in self._yahoo_ticker.info:
            return self._yahoo_ticker.info['trailingEps']
        return None

    @property
    def forward_eps(self) -> float | None:
        """
        Forward P/E ratio
        """
        if 'forwardEps' in self._yahoo_ticker.info:
            return self._yahoo_ticker.info['forwardEps']
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
            return self._yahoo_ticker.info['debtToEquity'] / 100
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
        # Consider operating revenue rather than total revenue
        return self._yahoo_ticker.income_stmt \
            .loc['Total Revenue'].sort_index().dropna()

    @property
    def revenue_growth(self) -> float:
        """
        Revenue growth
        """
        cagr = get_cagr(self.annual_revenue)
        avg = get_avg_pct_change(self.annual_revenue)
        forecast = get_linear_forecast(self.annual_revenue, years_forecast=2) \
            .iloc[0] / self.annual_revenue.iloc[-1] - 1
        # quarterly = self._yahoo_ticker.quarterly_income_stmt \
        #     .loc['Total Revenue'].sort_index().dropna() \
        #     .astype(float).pct_change(periods=4).dropna() \
        #     .iloc[-1]
        return min(x for x in (cagr, avg, forecast) if x is not None)

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

    @property
    def annual_net_income(self) -> pd.Series:
        """
        Annual net income
        """
        return self._yahoo_ticker.income_stmt \
            .loc['Net Income'].sort_index().dropna()

    # ----------------------------------------------------------------------------
    # Cash flow statement
    # ----------------------------------------------------------------------------

    @property
    def price_to_cash_flow(self) -> float:
        """
        Price-to-Cash-Flow (P/OCF)
        Below 10
        """
        # TODO return self.market_cap / 
        # self._yahoo_ticker.get_cash_flow().iloc[0]

    @property
    def weighted_average_cost_of_capital(self) -> float:
        """
        Weighted average cost of capital

        Docs:
        - https://www.investopedia.com/terms/w/wacc.asp
        - https://corporatefinanceinstitute.com/resources/valuation/what-is-wacc-formula/  # noqa
        """
        try:
            # Total Debt (Average over past 3 years)
            total_debt = self._yahoo_ticker.balance_sheet \
                .loc['Total Debt'].values[:3].mean()  # average of last 3 years
            net_debt = self._yahoo_ticker.balance_sheet \
                .loc['Net Debt'].values[:3].mean()

            # Tax Rate - Average of last 3 years
            tax_rate = self._yahoo_ticker.income_stmt \
                .loc['Tax Rate For Calcs'].values[:3].mean()

            # Interest Expense - Average over past 3 years
            interest_expense = self._yahoo_ticker.income_stmt \
                .loc['Interest Expense'].values[:3].mean()

            # Cost of Debt (after-tax)
            cost_of_debt = (interest_expense / total_debt) * (1 - tax_rate) \
                if total_debt else 0

            # Cost of Equity (CAPM)
            cost_of_equity = get_risk_free_rate(self.financial_currency) \
                + self.beta * get_market_risk_premium()

            # Debt and Equity Weights
            equity_weight = self.market_cap / (self.market_cap + net_debt)
            debt_weight = net_debt / (self.market_cap + net_debt)

            # WACC Calculation
            wacc = (equity_weight * cost_of_equity) \
                + (debt_weight * cost_of_debt)
        except KeyError:
            wacc = 0.08
        return wacc

    @property
    def intrinsic_value_per_share(self) -> float:
        """
        Intrinsic value per share
        """
        # Extract the Free Cash Flow (FCF) for the last few years
        fcf = self._yahoo_ticker.cash_flow \
            .loc['Free Cash Flow'].sort_index().dropna()

        intrinsic_value = get_intrinsinc_value(
            fcf,
            risk_free_rate=get_risk_free_rate(
                self.financial_currency),
            wacc=self.weighted_average_cost_of_capital,
            years_forecast=5)

        # Get the exchange rate
        exchange_rate = 1  # TODO get_exchange_rate(
        # self.currency, self.financial_currency)

        # Calculate the intrinsic stock price
        return exchange_rate * intrinsic_value \
            / self.shares_outstanding

    @property
    def graham_value_per_share(self) -> float:
        """
        Benjamin Graham's value per share
        """
        # TODO calculate EPS growth rate
        eps_growth_rate = self.revenue_growth  # TODO

        # Graham uses the current yield of AAA corp bonds
        risk_free_rate = get_risk_free_rate(self.currency)

        # Get the exchange rate because the financial_currency
        # of EPS is not necessaruily the currency of previous_close
        exchange_rate = 1  # TODO get_exchange_rate(
        # self.currency, self.financial_currency)

        if isinstance(self.trailing_eps, float):
            return exchange_rate * self.trailing_eps \
                * (8.5 + 2 * eps_growth_rate) \
                / risk_free_rate
        return None

    # ----------------------------------------------------------------------------
    # Analyst data
    # ----------------------------------------------------------------------------

    def analyst_recommendation(self) -> str:
        """
        Analyst recommendation
        """
        # return self._yahoo_ticker.recommendations

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
            'revenue_growth': self.revenue_growth,
            # 'gross_margin_avg': self.gross_margin_avg,
            # 'selling_general_and_admin_ratio':
            #   self.selling_general_and_admin_ratio,
            # 'research_and_development_ratio':
            #   self.research_and_development_ratio,
            # -------- Cash flow statement
            'weighted_average_cost_of_capital': \
            self.weighted_average_cost_of_capital,
            'intrinsic_value_per_share': self.intrinsic_value_per_share,
            'delta_intrinsic_value': \
            self.intrinsic_value_per_share / self.previous_close - 1 \
            if isinstance(self.intrinsic_value_per_share, float) else None,
            'graham_value_per_share': self.graham_value_per_share,
            'delta_graham_value': \
            self.graham_value_per_share / self.previous_close - 1 \
            if isinstance(self.graham_value_per_share, float) else None,
            # -------- Analyst data
            # 'analyst_recommendation': self.analyst_recommendation(),
            # -------- Statistics
            'rsi_14': super().rsi_14,
            })
