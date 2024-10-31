import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pydantic import BaseModel

import yfinance as yf

class Asset(BaseModel):
    def __init__(self, ticker: str):
        self._yahoo_ticker = yf.Ticker(ticker)
        
    @property
    def yahoo_ticker(self):
        return self._yahoo_ticker
    
    @property
    def symbol(self):
        return self._yahoo_ticker.info['symbol']
    


    