from enum import Enum
import matplotlib as plt
import seaborn as sns
import yfinance as yf

# import finance as fin
from . import finance

Frequency = Enum('Frequency', ['D', 'W', 'M'])

# ------------------------------------------------------------------------------
# Single-Security Time Series
# ------------------------------------------------------------------------------
class SingleTimeSeries:
    def __init__(self, ticker, years:int= 5, frequency:Frequency= Frequency.W):
        '''
        Constructor
        '''
        self.ticker = ticker
        self.years = years
        # self.currency = currency,
        self.frequency = frequency

    # load/save from file

    # pull history from yahoo (possibly use providers)
    def history(self):
        '''
        Pull data from provider
        '''
        ticker = yf.Ticker(self.ticker)
        period = f'{self.years}y'
        if self.frequency == Frequency.D:
            interval = '1d'
        elif self.frequency == Frequency.W:
            interval = '1wk'
        else:
            interval = '1mo'
        self.data = ticker.history(period=period, interval=interval, auto_adjust=True)
        # When auto_adjust == True, Close is actually Adj Close
        # as defined by CRSP rules: https://help.yahoo.com/kb/adjusted-close-sln28256.html
        # See also https://github.com/ranaroussi/yfinance/issues/1333
        self.data.index = self.data.index.tz_localize(None).to_period(self.frequency.name)
        self.data['Return'] = self.data[['Close']].pct_change()
        self.data.dropna()
        return self.data
    
    def stats(self, rf=0):
        '''
        Show stats
        '''
        df = self.data[['Return']].dropna()
        return finance.summary_stats(df, rf)
    
    def plot(self, y_col='Close'):
        '''
        Plt data
        '''
        df = self.data[[y_col]].dropna()
        plot = df.plot()
        plot.set_title(self.ticker)
        plot.set_ylabel(y_col)

# ------------------------------------------------------------------------------
# Multi-Security Time Series
# ------------------------------------------------------------------------------
class MultiTimeSeries:
    def __init__(self, tickers, years:int= 5, frequency:Frequency= Frequency.W):
        '''
        Constructor
        '''
        self.tickers = tickers
        self.years = years
        # self.currency = currency,
        self.frequency = frequency

    # load/save from file

    # pull from yahoo (possibly use providers)
    def history(self):
        '''
        Pull data from provider
        '''
        tickers = yf.Tickers(self.tickers)
        period = f'{self.years}y'
        if self.frequency == Frequency.D:
            interval = '1d'
        elif self.frequency == Frequency.W:
            interval = '1wk'
        else:
            interval = '1mo'
        self.data = tickers.history(period=period, interval=interval, auto_adjust=True) # group_by='ticker'
        # When auto_adjust == True, Close is actually Adj Close
        # as defined by CRSP rules: https://help.yahoo.com/kb/adjusted-close-sln28256.html
        # See also https://github.com/ranaroussi/yfinance/issues/1333
        self.data.index = self.data.index.tz_localize(None).to_period(self.frequency.name)
        # https://stackoverflow.com/questions/63107594/how-to-deal-with-multi-level-column-names-downloaded-with-yfinance/63107801#63107801
        self.data = self.data.join(self.data[['Close']].pct_change().rename(columns={'Close':'Return'}))
        return self.data
    
    def stats(self, rf=0):
        '''
        Show stats (TODO scale to start at 100)
        '''
        df = self.data[['Return']].dropna().droplevel(0, axis=1)
        return finance.summary_stats(df, rf)
    
    def plot(self):
        '''
        Plot data series starting at base 100
        '''
        df = self.data['Return'].dropna() #.droplevel(0, axis=1)
        df = 100 * (df+1).cumprod()
        plot = df.plot()
        plot.set_title(self.tickers)
        plot.set_ylabel('Return')

    def plot_corr(self):
        '''
        Plot correlaion heatmap
        '''
        df = self.data[['Return']].dropna().droplevel(0, axis=1)
        corr= df.corr()
        sns.heatmap(corr, annot=True, fmt='.2f')

    def plot_ef(self, rf=0):
        df = self.data[['Return']].dropna().droplevel(0, axis=1)
        er = finance.annualize_rets(df)
        cov = df.cov()
        finance.plot_ef(n_points=36, er=er, cov=cov, rf=rf, legend=True, show_cml=True, show_ew=True, show_gmv=True)

    def plot_w(self, rf=0):
        df = self.data[['Return']].dropna().droplevel(0, axis=1)
        er = finance.annualize_rets(df)
        cov = df.cov()
        finance.plot_w(er=er, cov=cov, rf=rf)