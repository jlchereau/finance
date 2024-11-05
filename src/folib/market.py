"""
Market constants and functions
"""


import requests
import pandas as pd
from bs4 import BeautifulSoup


# Map of Exchange names to yfinance suffixes
EXCHANGE_SUFFIX_MAP = {
    'Asx - All Markets': '.AX',
    'Bolsa De Madrid': '.MC',
    'Borsa Italiana': '.MI',
    'Cboe BZX formerly known as BATS': '',  # A vérifier
    'Deutsche Boerse Xetra': '.DE',
    'Euronext Amsterdam': '.AS',
    'Hong Kong Exchanges And Clearing Ltd': '.HK',
    'Irish Stock Exchange - All Market': '.IR',
    'London Stock Exchange': '.L',
    'NASDAQ': '',
    'Nasdaq Omx Helsinki Ltd.': '.HE',
    'Nasdaq Omx Nordic': '.ST',  # A vérifier
    'New York Stock Exchange Inc.': '',
    'New Zealand Exchange Ltd': '.NZ',
    'Nyse Euronext - Euronext Brussels': '.BR',
    'Nyse Euronext - Euronext Lisbon': 'LS',
    'Nyse Euronext - Euronext Paris': '.PA',
    'Omx Nordic Exchange Copenhagen A/S': '.CO',
    'Oslo Bors Asa': '.OL',
    'SIX Swiss Exchange': '.SW',
    'Singapore Exchange': '.SI',
    'Tel Aviv Stock Exchange': '',
    'Tokyo Stock Exchange': '.T',
    'Toronto Stock Exchange': '.TO',
    'Wiener Boerse Ag': '.VI',
    'Xetra': '.DE'
}


def add_exchange_suffix(ticker: str, exchange: str) -> str:
    """
    Function to adjust tickers based on the exchange
    """
    # Trim any whitespace from ticker and exchange
    ticker = str(ticker).strip().replace(' ', '-')
    exchange = str(exchange).strip()  # .upper()
    # Get the suffix for the exchange, default to empty string
    suffix = EXCHANGE_SUFFIX_MAP.get(exchange, '')
    # Adjust ticker for special cases
    if exchange == 'Hong Kong Exchanges And Clearing Ltd':
        # For Hong Kong, tickers need to be zero-padded to 4 digits
        ticker = ticker.zfill(4)
    elif exchange == 'Tokyo Stock Exchange':
        # For Tokyo Stock Exchange, tickers are numeric
        ticker = ticker.strip()
    # elif exchange == 'KOREA EXCHANGE':
        # For Korea, tickers need to be zero-padded to 6 digits
        # ticker = ticker.zfill(6)
    # elif exchange == 'SHANGHAI STOCK EXCHANGE':
        # For Shanghai Stock Exchange
        # ticker = ticker.strip()
    # elif exchange == 'SHENZHEN STOCK EXCHANGE':
        # For Shenzhen Stock Exchange
        # ticker = ticker.strip()
    return ticker + suffix


# ----------------------------------------------------------------------------
# Lists of tickers
# ----------------------------------------------------------------------------


def get_sp500_tickers() -> list:
    """
    Get a list of S&P 500 tickers
    """
    sp500_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    # The first table contains the tickers
    sp500_table = pd.read_html(sp500_url, header=0)[0]
    sp500_tickers = sp500_table['Symbol'] \
        .str.replace('.', '-', regex=False).tolist()
    return sp500_tickers


def get_nasdaq100_tickers() -> list:
    """
    Get a list of nasdaq 100 tickers
    """
    nasdaq100_url = 'https://en.wikipedia.org/wiki/NASDAQ-100'
    # The fifth table contains the tickers
    nasdaq100_table = pd.read_html(nasdaq100_url, header=0)[4]
    nasdaq100_tickers = nasdaq100_table['Symbol'] \
        .tolist()
    return nasdaq100_tickers


def get_msci_world_tickers() -> list:
    """
    Get a list of MSCI World tickers
    """
    url = 'https://www.blackrock.com/uk/individual/products/251882/' \
        'ishares-msci-world-ucits-etf-acc-fund/1527484370694.ajax?' \
        'fileType=xls&fileName=iShares-Core-MSCI-World-UCITS-ETF_fund' \
        '&dataType=fund'
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    xml_content = response.content
    soup = BeautifulSoup(xml_content, 'xml')
    # Define the namespace prefix 'ss' to match
    #  'urn:schemas-microsoft-com:office:spreadsheet' namespace
    # namespace = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}
    # Find the Table element within the Worksheet
    table = soup.find('ss:Table')  # , namespaces=namespace)
    # Initialize a list to hold all rows of data
    data = []
    # Iterate over each Row in the Table
    for row in table.find_all('ss:Row'):  # , namespaces=namespace):
        row_data = []
        for cell in row.find_all('ss:Cell'):  # , namespaces=namespace):
            cell_data = cell.find('ss:Data')  # , namespaces=namespace)
            if cell_data:
                value = cell_data.text
            else:
                value = None
            row_data.append(value)
        data.append(row_data)
    # Convert the data into a pandas DataFrame
    data = pd.DataFrame(data)
    # Find the index of the header row
    #  (the row that contains 'Issuer Ticker')
    header_row_index = None
    for i, row in data.iterrows():
        if 'Issuer Ticker' in row.values:
            header_row_index = i
            break
    if header_row_index is None:
        raise RuntimeError("Header row not found.")
    # Extract headers and data
    headers = data.iloc[header_row_index].tolist()
    # Data starts after the header row
    data = data.iloc[header_row_index + 1:]
    data.columns = headers  # Set the column names
    data.reset_index(drop=True, inplace=True)
    # Remove rows where:
    # - 'Market Value' is None or'---' (to exclude totals and footnotes)
    # - 'Asset Class' is not 'Equity' to remove Cash and Derivatives
    data = data[data['Market Value'].notna()
                & (data['Market Value'] != '---')
                & (data['Asset Class'] == 'Equity')]
    # Optional: Remove any columns with all NaN values
    data.dropna(axis=1, how='all', inplace=True)
    # Apply the function to adjust tickers
    data['Ticker'] = data.apply(lambda r: add_exchange_suffix(
        r['Issuer Ticker'], r['Exchange']), axis=1)
    # Drop rows where Ticker is None
    data = data[data['Ticker'].notna()]  # raise error ???
    # Reset the index
    data.reset_index(drop=True, inplace=True)
    # Get a list of tickers for yahoo
    msci_world_tickers = data['Ticker'].to_list()
    return msci_world_tickers


def get_risk_free_rate(currency: str = 'USD') -> float:
    """
    Risk-free rate

    Proxies recommended by ChatGPT:
        - EUR: [LYQ2.DE ETF (Lyxor Euro Government Bond 1-3M DR UCITS ETF)]
        (https://finance.yahoo.com/quote/LYQ2.DE/)
        - USD: [BIL ETF (SPDR Bloomberg 1-3 Month T-Bill ETF)]
        (https://finance.yahoo.com/quote/BIL/)

    """
    if currency == 'USD':
        return 0.03  # Improve using BIL etf
    elif currency == 'EUR':
        return 0.02  # Improve
    else:
        raise ValueError('Currency not supported')


def get_market_risk_premium() -> float:
    """
    Market risk premium
    """
    return 0.05

# ----------------------------------------------------------------------------
# Fear gauges
# ----------------------------------------------------------------------------
