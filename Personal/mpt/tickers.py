from enum import Enum

# Todos IWLE SLDP IHYG INRG


# Tickers

Currency = Enum('Currency', ['EUR', 'GBP', 'USD'])
Type = Enum('Type', ['Stocks', 'Bonds', 'Commodities', 'Currencies'])

class Security:
    def __init__(self, ticker, name, currency, type):
        self.ticker = ticker
        self.name = name,
        self.currency = currency,
        self.type = type

# -------------
# Currencies
# -------------

USD_EXR = Security(
    ticker = 'EURUSD',
    name = 'EURUSD',
    currency = Currency.EUR,
    type = Type.Currencies
)

GBP_EXR = Security(
    ticker = 'EURGBP',
    name = 'EURGBP',
    currency = Currency.EUR,
    type = Type.Currencies
)

## -------------
## Stocks
## -------------

### EUR Stock ETFs

# https://www.ishares.com/uk/individual/en/products/251861/ishares-msci-europe-ucits-etf-acc-fund
SMEA_ETF = Security(
    ticker = 'SMEA',
    name = 'iShares Core MSCI Europe UCITS ETF EUR (Acc)',
    currency = Currency.EUR,
    type = Type.Stocks
)

# https://www.ishares.com/uk/individual/en/products/251787/ishares-euro-dividend-ucits-etf
IDVY_ETF = Security(
    ticker = 'IDVY',
    name = '',
    currency = Currency.EUR,
    type = Type.Stocks
)

### USD Stock ETFs

SPY_ETF = Security(
    ticker = 'SPY',
    name = '',
    currency = Currency.USD,
    type = Type.Stocks
)

### Industry Specific

# https://www.ishares.com/ch/professionals/en/products/325781/ishares-listed-private-equity-ucits-etf
PRIVATE_EQUITY = Security(
    ticker = 'IPRA.AS',
    name = '',
    currency = Currency.USD,
    type = Type.Stocks
)



## -------------
## Bonds
## -------------

### EUR Bond ETFs

# https://www.ishares.com/uk/individual/en/products/251565/ishares-euro-corporate-bond-large-cap-ucits-etf
IBCX_ETF = Security(
    ticker = 'IBCX.L',
    name = '',
    currency = Currency.EUR,
    type = Type.Bonds
)

# https://www.blackrock.com/fr/intermediaries/products/251726/ishares-euro-corporate-bond-ucits-etf - TODO Switch to IEAA 
IEAC_ETF = Security(
    ticker = 'IEAC.L',
    name = '',
    currency = Currency.EUR,
    type = Type.Bonds
)

### USD Bond ETFs

AGG_ETF = Security(
    ticker = 'AGG',
    name = '',
    currency = Currency.USD,
    type = Type.Bonds
)

BND_ETF = Security(
    ticker = 'BND',
    name = '',
    currency = Currency.USD,
    type = Type.Bonds
)

### GBP Bond ETFs

# https://www.ishares.com/uk/individual/en/products/251841/ishares-corporate-bond-exfinancials-ucits-etf
ISXF_ETF = Security(
    ticker = 'ISXF',
    name = '',
    currency = Currency.GBP,
    type = Type.Bonds
)

# https://www.ishares.com/uk/individual/en/products/251839/ishares-corporate-bond-ucits-etf
SLXX_ETF = Security(
    ticker = 'SLXX',
    name = '',
    currency = Currency.GBP,
    type = Type.Bonds
)


## -------------
## Real Estate
## -------------



## -------------
## Commodities (incl. Precious Metals)
## -------------

