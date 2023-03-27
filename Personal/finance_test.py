import numpy as np
import pandas as pd
import mpt.finance as finance
import scipy.stats as stats

# create test data
a = 0.01
b = 0.02
y = 5
ppy = 12
p = ppy * y
idx_monthly = pd.period_range(start='2018-01', periods=p, freq='M')
df_monthly = pd.DataFrame([[a, b]], index=idx_monthly, columns=['A', 'B'])

# compound
def test_compound():
    r = df_monthly.copy()
    assert round(finance.compound(r).A, 6) == round((1 + a)**p - 1, 6)
    assert round(finance.compound(r).B, 6) == round((1 + b)**p - 1, 6)

# periods_per_year
def test_periods_per_year():
    r = df_monthly.copy()
    assert finance.periods_per_year(r) == ppy
    # TODO daily = 252? what about european markets?
    # TODO raise error?

# annualized returns
def test_annualize_rets():
    r = df_monthly.copy()
    assert finance.annualize_rets(r).A == ((1 + r).prod()**(1/y) - 1).A

# anualized volatility
def test_annualize_vol():
    r = df_monthly.copy()
    assert finance.annualize_vol(r).A == (r.std()*(ppy**0.5)).A

# skewness
def test_skewness():
    r = df_monthly[['A']].copy()
    r['A'] = np.random.random(size=len(r))
    assert round(finance.skewness(r).A, 10) == round(stats.skew(r)[0], 10)

# kurtosis
def test_kurtosis():
    r = df_monthly[['A']].copy()
    r['A'] = np.random.random(size=len(r))
    assert round(finance.kurtosis(r).A, 10) == round(stats.kurtosis(r, fisher=False)[0], 10)

# drawdawn
def test_drawdawn():
    r = df_monthly.copy()
    assert finance.drawdown(r).A == 0

# sharpe ratio
def test_sharpe_ratio():
    r = df_monthly.copy()
    assert finance.sharpe_ratio(r, 0).A == 0
