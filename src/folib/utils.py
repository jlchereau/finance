"""
Utility constants and functions
"""


from enum import Enum
import pandas as pd
import yfinance as yf
from .market import get_risk_free_rate, get_market_risk_premium


class AssetType(Enum):
    """
    Asset Type
    """
    EQUITY = 0
    ETF = 1


def get_sma(data: pd.Series, window: int = 14) -> pd.Series:
    """
    Simple moving average
    """
    return data.rolling(window=window).mean()


def get_ema(data: pd.Series, window: int = 14) -> pd.Series:
    """
    Exponential moving average
    """
    return data.ewm(span=window, adjust=False).mean()


def get_macd(data: pd.Series) -> pd.Series:
    """
    Moving average convergence divergence (MACD)
    """
    return get_ema(data, 12) - get_ema(data, 26)


def get_rsi(data: pd.Series, window: int = 14) -> pd.Series:
    """
    Relative strength index (RSI)
    """
    delta = data.diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    roll_up = up.rolling(window=window).mean()
    roll_down = down.abs().rolling(window=window).mean()
    rs = roll_up / roll_down
    return 100.0 - (100.0 / (1.0 + rs))


def get_bollinger_bands(data: pd.Series, window: int = 20) -> pd.DataFrame:
    """
    Bollinger bands
    """
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * 2)
    lower_band = rolling_mean - (rolling_std * 2)
    return pd.concat([upper_band, rolling_mean, lower_band], axis=1) \
        .rename(columns={0: 'upper', 1: 'middle', 2: 'lower'})


def get_cagr(data: pd.Series) -> float:
    """
    Compound annual growth rate
    """
    data.index = pd.to_datetime(data.index)
    data = data.astype(float).sort_index().dropna()
    assert len(data) > 1, 'Not enough data to calculate CAGR'
    start_value = data.iloc[0]
    end_value = data.iloc[-1]
    num_years = len(data) - 1
    return (end_value / start_value) ** (1 / num_years) - 1


def get_weighted_average_cost_of_capital(
        yahoo_ticker: yf.Ticker,
        risk_free_rate: float = get_risk_free_rate(),
        market_risk_premium: float = get_market_risk_premium()
        ) -> float:
    """
    Weighted average cost of capital
    """
    assert yahoo_ticker.info['quoteType'] == 'EQUITY', \
        f'{yahoo_ticker.info['symbol']} is not equity!'

    # Market Cap as proxy for Equity Value
    market_cap = yahoo_ticker.info['previousClose'] * \
        yahoo_ticker.info['sharesOutstanding']

    # Total Debt (Average over past 3 years)
    total_debt = yahoo_ticker.balance_sheet.loc['Total Debt'] \
        .values[:3].mean()  # average of last 3 years
    net_debt = yahoo_ticker.balance_sheet.loc['Net Debt'] \
        .values[:3].mean()

    # Beta (Assuming beta value is stable,
    # but could average across historical estimates if available)
    beta = yahoo_ticker.info['beta']

    # Tax Rate - Average of last 3 years
    tax_rate = yahoo_ticker.income_stmt.loc['Tax Rate For Calcs'] \
        .values[:3].mean()

    # Interest Expense - Average over past 3 years
    interest_expense = yahoo_ticker.income_stmt.loc['Interest Expense'] \
        .values[:3].mean()

    # Cost of Debt (after-tax, using average interest expense and total debt)
    cost_of_debt = (interest_expense / total_debt) * (1 - tax_rate) \
        if total_debt else 0

    # Cost of Equity (CAPM)
    cost_of_equity = risk_free_rate + beta * market_risk_premium

    # Debt and Equity Weights (averaged with Net Debt over past 3 years)
    equity_weight = market_cap / (market_cap + net_debt)
    debt_weight = net_debt / (market_cap + net_debt)

    # WACC Calculation
    wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt)
    return wacc


def get_intrinsinc_value(
        yahoo_ticker: yf.Ticker,
        growth_rate: float = 0.05,
        discount_rate: float = get_risk_free_rate(),
        ) -> float:
    """
    Intrinsic value
    """
    assert yahoo_ticker.info['quoteType'] == 'EQUITY', \
        f'{yahoo_ticker.info['symbol']} is not equity!'

    # Current market price
    current_price = yahoo_ticker.info['previousClose']

    # Number of years to project
    years = 10

    # Intrinsic value calculation
    intrinsic_value = current_price * \
        (1 + growth_rate) ** years / (1 + discount_rate) ** years

    return intrinsic_value
