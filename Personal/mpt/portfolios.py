import tickers as tk

# ideas from https://www.optimizedportfolio.com/

# IMPORTANT: Portfolios shoud not include weights => cf. Strategies

# 60/40 USD portfolio
portfolio_balanced_usd = {
    tk.SPY_ETF.ticker: 0.6,
    tk.AGG_ETF.ticker: 0.4
}

# 50/30/20 portfolio
# https://www.blackrock.com/us/financial-professionals/investment-strategies/alternative-investments
portfolio_alternative_usd = {
    tk.SPY_ETF.ticker: 0.5,
    tk.AGG_ETF.ticker: 0.3,
    # Private Equity
    # Alternative Investment
}

# https://www.marketwatch.com/story/this-simple-no-sweat-portfolio-makes-money-in-booms-and-slumps-11674141614
portfolio_aana_usd = {
    tk.SPY_ETF.ticker: 1/7, # SP500
    tk.IWM_ETF.ticker: 1/7, # Russel 2000
    tk.VEA_ETF.ticker: 1/7, # DM
    tk.VNQ_ETF.ticker: 1/7, # REIT
    tk.IEF_ETF.ticker: 1/7, # TBonds 7-10
    tk.GSG_ETF.ticker: 1/7, # Commodities
    tk.SGOL_ETF.ticker: 1/7 # Gold
}

