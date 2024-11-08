"""
Utility constants and functions
"""


import numpy as np
import pandas as pd
import statsmodels.api as sm


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


def get_cagr(data: pd.Series) -> float | None:
    """
    Compound annual growth rate
    """
    data.index = pd.to_datetime(data.index)
    data = data.astype(float).sort_index().dropna()
    if len(data) < 2:  # Not enough data to calculate CAGR
        return None
    start_value = data.iloc[0]
    end_value = data.iloc[-1]
    num_years = len(data) - 1
    return (end_value / start_value) ** (1 / num_years) - 1


def get_avg_pct_change(data: pd.Series) -> float | None:
    """
    Average percentage change
    """
    data.index = pd.to_datetime(data.index)
    data = data.astype(float).sort_index().dropna()
    if len(data) < 2:  # Not enough data for pct_change
        return None
    return data.pct_change().mean()


def get_linear_forecast(data: pd.Series, years_forecast: int = 5) -> pd.Series:
    """
    Linear forecast (data is annual)
    """
    x = data.index.year.values
    y = data.values
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    forecast_x = np.arange(data.index.year.max() + 1,
                           data.index.year.max() + years_forecast + 1)
    # years_forecast=1 does not work
    # https://stackoverflow.com/questions/48514035/ols-predict-one-value-array
    forecast_x = sm.add_constant(forecast_x)
    forecast_y = model.predict(forecast_x)
    forecast_index = pd.date_range(start=data.index[-1]
                                   + pd.DateOffset(years=1),
                                   periods=years_forecast, freq='YE')
    return pd.Series(forecast_y, index=forecast_index)


def get_intrinsinc_value(
        fcf: pd.Series,
        risk_free_rate: float = 0.03,
        wacc: float = 0.08,
        years_forecast: int = 5
        ) -> float:
    """
    Intrinsic value
    """
    # Forecast Free Cash Flows for the next years_forecast (5 to 10 years)
    fcf_forecast = get_linear_forecast(fcf, years_forecast)

    # Discount the Free Cash Flows to the present value
    # Note: npv from numpy_financial starts with current year
    # which is not part of forecasts so we compute it ourselves
    discounted_fcf = 0
    for i in range(1, years_forecast + 1):
        discounted_fcf += fcf_forecast.iloc[i-1] / (1 + wacc) ** i

    # Calculate the terminal value using the perpetuity method
    terminal_value = fcf_forecast.iloc[-1] * (1 + risk_free_rate) \
        / (wacc - risk_free_rate)

    # Discount the terminal value to present value
    terminal_value_discounted = \
        terminal_value / (1 + wacc) ** years_forecast

    # Calculate the Total Enterprise Value (TEV)
    # by summing discounted FCF and terminal value
    total_enterprise_value = discounted_fcf + terminal_value_discounted

    # This is our intrinsic value
    return total_enterprise_value
