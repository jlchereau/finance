# ***************************************************************************************
# My Modern Portfolio Theory library (mptlib)
# ***************************************************************************************

import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import minimize

# TODO resample

# ---------------------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------------------

# compounded returns
def compound(r: pd.Series):
    """
    returns the result of compounding the set of returns in r
    """
    return np.expm1(np.log1p(r).sum())

# periods per year
def periods_per_year(r: pd.Series):
    """
    returns the number of periods per year in a timeseries
    """
    if r.index.freqstr == 'M':
        return 12
    if r.index.freqstr == 'W' or r.index.freqstr == 'W-SUN':
        return 52
    if r.index.freqstr == 'D':
        return 252
    # leap years?
    # non-US exchanges?
    raise ValueError('r should be a timeseries with a monthly, weekly or daily frequency')

# annualized returns
def annualize_rets(r: pd.Series):
    """
    Annualizes a set of returns
    """
    # compounded_growth = (1+r).prod()
    compounded_growth = 1 + compound(r)
    n_periods = r.shape[0]
    y_periods = periods_per_year(r)
    return compounded_growth**(y_periods/n_periods) - 1

# anualized volatility
def annualize_vol(r: pd.Series):
    """
    Annualizes the vol of a set of returns
    """
    y_periods = periods_per_year(r)
    # return r.std()*(y_periods**0.5)
    return r.std(ddof=0)*np.sqrt(y_periods)

# skewness
def skewness(r: pd.Series):
    """
    Alternative to scipy.stats.skew()
    Computes the skewness of the supplied Series or DataFrame
    Returns a float or a Series
    """
    demeaned_r = r - r.mean()
    # use the population standard deviation, so set dof=0
    sigma_r = r.std(ddof=0)
    exp = (demeaned_r**3).mean()
    return exp/sigma_r**3

# kurtosis
def kurtosis(r: pd.Series):
    """
    Alternative to scipy.stats.kurtosis() with fisher=False
    Computes the kurtosis of the supplied Series or DataFrame
    Returns a float or a Series
    """
    demeaned_r = r - r.mean()
    # use the population standard deviation, so set dof=0
    sigma_r = r.std(ddof=0)
    exp = (demeaned_r**4).mean()
    return exp/sigma_r**4
                         
# max drawdown
def drawdown(r: pd.Series):
    """
    Computes the maximum drawdown
    """
    # r is a return vector
    wealth = (r+1).cumprod()
    # determine cumulative maximum value
    cummax = wealth.cummax()
    # calculate drawdown vector
    drawdown = wealth/cummax - 1
    return drawdown.min()


# sharpe ratio - https://awgmain.morningstar.com/webhelp/glossary_definitions/mutual_fund/mfglossary_Sharpe_Ratio.html
def sharpe_ratio(r: pd.Series, rf=0):
    """
    Computes the annualized sharpe ratio of a set of returns and risk free rates
    provided as a single numeric value or as a time series
    """
    n_periods = r.shape[0]
    y_periods = periods_per_year(r)
    if type(rf) is float or type(rf) is int:
        # convert the annual riskfree rate to per period
        rf = (1+rf)**(1/y_periods)-1
    else:
        if rf.index.freqstr != r.index.freqstr:
            raise ValueError('time series have incompatible frequencies')
        if rf.shape[0] != n_periods:
            raise ValueError('time series have incompatible lengths')
        if rf.index[0] != r.index[0]:
            raise ValueError('time series have incompatible first periods')
    excess_ret = r - rf
    avg_excess_ret = np.sum(excess_ret)/n_periods
    # ann_excess_ret = annualize_rets(excess_ret)
    ann_excess_ret = (avg_excess_ret + 1)**y_periods - 1
    ann_vol = annualize_vol(excess_ret)
    return ann_excess_ret/ann_vol

# TODO adjusted sharpe ratio

# Cornish Fisher VaR (Value at Risk)
def var_gaussian(r, level=5, modified=False):
    """
    Returns the Parametric Gauusian VaR of a Series or DataFrame
    If "modified" is True, then the modified VaR is returned,
    using the Cornish-Fisher modification
    """
    # compute the Z score assuming it was Gaussian
    z = norm.ppf(level/100)
    if modified:
        # modify the Z score based on observed skewness and kurtosis
        s = skewness(r)
        k = kurtosis(r)
        z = (z +
                (z**2 - 1)*s/6 +
                (z**3 -3*z)*(k-3)/24 -
                (2*z**3 - 5*z)*(s**2)/36
            )
    return -(r.mean() + z*r.std(ddof=0))

def var_historic(r, level=5):
    """
    Returns the historic Value at Risk at a specified level
    i.e. returns the number such that "level" percent of the returns
    fall below that number, and the (100-level) percent are above
    """
    if isinstance(r, pd.DataFrame):
        return r.aggregate(var_historic, level=level)
    elif isinstance(r, pd.Series):
        return -np.percentile(r, level)
    else:
        raise TypeError("Expected r to be a Series or DataFrame")

# Historic CVaR
def cvar_historic(r, level=5):
    """
    Computes the Conditional VaR of Series or DataFrame
    """
    if isinstance(r, pd.Series):
        is_beyond = r <= -var_historic(r, level=level)
        return -r[is_beyond].mean()
    elif isinstance(r, pd.DataFrame):
        return r.aggregate(cvar_historic, level=level)
    else:
        raise TypeError("Expected r to be a Series or DataFrame")

# TODO sortino ratio - https://www.codearmo.com/blog/sharpe-sortino-and-calmar-ratios-python

# TODO treynor ratio

# TODO calmar ratio - https://www.codearmo.com/blog/sharpe-sortino-and-calmar-ratios-python

# summary statistics
def summary_stats(r: pd.DataFrame, rf):
    """
    Return a DataFrame that contains aggregated summary stats for the returns in the columns of r
    """
    ann_r = r.aggregate(annualize_rets)
    ann_vol = r.aggregate(annualize_vol)
    ann_sr = r.aggregate(sharpe_ratio, rf=rf)
    dd = r.aggregate(drawdown)
    skew = r.aggregate(skewness)
    kurt = r.aggregate(kurtosis)
    cf_var5 = r.aggregate(var_gaussian, modified=True)
    hist_cvar5 = r.aggregate(cvar_historic)
    return pd.DataFrame({
        "Annualized Return": ann_r,
        "Annualized Vol": ann_vol,
        "Skewness": skew,
        "Kurtosis": kurt,
        "Cornish-Fisher VaR (5%)": cf_var5,
        "Historic CVaR (5%)": hist_cvar5,
        "Sharpe Ratio": ann_sr,
        "Max Drawdown": dd
    })

def portfolio_return(w, er):
    """
    Computes the return on a portfolio from constituent returns and weights
    weights are a numpy array or Nx1 matrix and returns are a numpy array or Nx1 matrix
    """
    return w.T @ er

def portfolio_vol(w, cov):
    """
    Computes the vol of a portfolio from a covariance matrix and constituent weights
    weights are a numpy array or N x 1 matrix and cov is an N x N matrix
    """
    return np.sqrt(w.T @ cov @ w)

def minimize_vol(target_return, er, cov):
    """
    Returns the optimal weights that achieve the target return
    given a set of expected returns and a covariance matrix
    """
    n = er.shape[0]
    init_guess = np.repeat(1/n, n)
    bounds = ((0.0, 1.0),) * n # an N-tuple of 2-tuples!
    # construct the constraints
    weights_sum_to_1 = {'type': 'eq',
                        'fun': lambda w: np.sum(w) - 1
    }
    return_is_target = {'type': 'eq',
                        'args': (er,),
                        'fun': lambda w, er: target_return - portfolio_return(w, er)
    }
    weights = minimize(portfolio_vol, init_guess,
                       args=(cov,), method='SLSQP',
                       options={'disp': False},
                       constraints=(weights_sum_to_1, return_is_target),
                       bounds=bounds)
    return weights.x

# def tracking_error(r_a, r_b):
#    """
#    Returns the Tracking Error between the two return series
#    """
#    return np.sqrt(((r_a - r_b)**2).sum())
                         
def msr(rf, er, cov):
    """
    Returns the weights of the portfolio that gives you the maximum sharpe ratio
    given the riskfree rate and expected returns and a covariance matrix
    """
    n = er.shape[0]
    init_guess = np.repeat(1/n, n)
    bounds = ((0.0, 1.0),) * n # an N-tuple of 2-tuples!
    # construct the constraints
    weights_sum_to_1 = {'type': 'eq',
                        'fun': lambda w: np.sum(w) - 1
    }
    def neg_sharpe(w, rf, er, cov):
        """
        Returns the negative of the sharpe ratio
        of the given portfolio
        """
        r_p = portfolio_return(w, er)
        vol_p = portfolio_vol(w, cov)
        return -(r_p - rf)/vol_p
    
    weights = minimize(neg_sharpe, init_guess,
                       args=(rf, er, cov), method='SLSQP',
                       options={'disp': False},
                       constraints=(weights_sum_to_1,),
                       bounds=bounds)
    return weights.x

def gmv(cov):
    """
    Returns the weights of the Global Minimum Volatility portfolio
    given a covariance matrix
    """
    n = cov.shape[0]
    return msr(0, np.repeat(1, n), cov)

def optimal_weights(n_points, er, cov):
    """
    Returns a list of weights that represent a grid of n_points on the efficient frontier
    """
    target_rs = np.linspace(er.min(), er.max(), n_points)
    weights = [minimize_vol(target_return, er, cov) for target_return in target_rs]
    return weights

def plot_ef(n_points, er, cov, rf=0, style='.-', legend=False, show_cml=False, show_ew=False, show_gmv=False):
    """
    Plots the multi-asset efficient frontier
    """
    weights = optimal_weights(n_points, er, cov)
    rets = [portfolio_return(w, er) for w in weights]
    vols = [portfolio_vol(w, cov) for w in weights]
    ef = pd.DataFrame({
        "Returns": rets, 
        "Volatility": vols
    })
    ax = ef.plot.line(x="Volatility", y="Returns", style=style, legend=legend)
    if show_cml:
        ax.set_xlim(left = 0)
        # get MSR
        w_msr = msr(rf, er, cov)
        r_msr = portfolio_return(w_msr, er)
        vol_msr = portfolio_vol(w_msr, cov)
        # add CML
        cml_x = [0, vol_msr]
        cml_y = [rf, r_msr]
        ax.plot(cml_x, cml_y, color='green', marker='o', linestyle='dashed', linewidth=2, markersize=10)
    if show_ew:
        n = er.shape[0]
        w_ew = np.repeat(1/n, n)
        r_ew = portfolio_return(w_ew, er)
        vol_ew = portfolio_vol(w_ew, cov)
        # add EW
        ax.plot([vol_ew], [r_ew], color='goldenrod', marker='o', markersize=10)
    if show_gmv:
        w_gmv = gmv(cov)
        r_gmv = portfolio_return(w_gmv, er)
        vol_gmv = portfolio_vol(w_gmv, cov)
        # add EW
        ax.plot([vol_gmv], [r_gmv], color='midnightblue', marker='o', markersize=10)  
    return ax

def plot_w(er, cov, rf=0):
    #wts = pd.DataFrame({
    #    "EW": erk.weight_ew(ind_rets["2016":]),
    #    "CW": erk.weight_cw(ind_rets["2016":], cap_weights=ind_mcap),
    #    "GMV-Sample": weight_gmv(ind_rets["2016":], cov_estimator=sample_cov),
    #    "GMV-ConstCorr": weight_gmv(ind_rets["2016":], cov_estimator=cc_cov),
    #})
    n = er.shape[0]
    wts = pd.DataFrame(
        data={
            "EW": np.repeat(1/n, n),
            "GMV": gmv(cov),
            "MSR": msr(rf, er, cov)
        },
        index=er.index
    )
    print(wts)
    wts.T.plot.bar(stacked=True, figsize=(15,6), legend=True);