"""
File containing tool functions for the different agents in the graph.
"""
import pandas as pd
import yfinance as yf
import datetime as dt

from typing import Union, Dict
from langchain_core.tools import tool

from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD
from ta.volume import volume_weighted_average_price

import serpapi
from dotenv import load_dotenv
load_dotenv()

######## TECHNICAL AGENT TOOLS ########
@tool("get_stock_prices")
def get_stock_prices(stock_ticker: str) -> Union[Dict, str]:
    """Fetches historical stock price data and technical indicator for a given stock_ticker."""
    try:
        # get stock data from yahoo finance and store them in a dataframe
        data = yf.download(
            stock_ticker,
            start=dt.datetime.now() - dt.timedelta(weeks=24*3),
            end=dt.datetime.now(),
            interval='1wk'
        )
        df = data.copy()
        data.reset_index(inplace=True)
        data.Date = data.Date.astype(str)
        
        # get separate series objects from the dataframe
        close = pd.Series(df['Close'].squeeze(), index=df['Close'].index)
        high = pd.Series(df['High'].squeeze(), index=df['High'].index)
        low =  pd.Series(df['Low'].squeeze(), index=df['Low'].index)
        volume = pd.Series(df['Volume'].squeeze(), index=df['Volume'].index)

        # compute technical indicators and store them in a dictionary
        indicators = {}
        rsi_series = RSIIndicator(close, window=14).rsi().iloc[-12:]
        indicators["RSI"] = {date.strftime('%Y-%m-%d'): int(value) 
                    for date, value in rsi_series.dropna().to_dict().items()}
        
        sto_series = StochasticOscillator(
            high, low, close, window=14).stoch().iloc[-12:]
        indicators["Stochastic_Oscillator"] = {
                    date.strftime('%Y-%m-%d'): int(value) 
                    for date, value in sto_series.dropna().to_dict().items()}

        macd = MACD(close)
        macd_series = macd.macd().iloc[-12:]
        indicators["MACD"] = {date.strftime('%Y-%m-%d'): int(value) 
                    for date, value in macd_series.to_dict().items()}
        
        macd_signal_series = macd.macd_signal().iloc[-12:]
        indicators["MACD_Signal"] = {date.strftime('%Y-%m-%d'): int(value) 
                    for date, value in macd_signal_series.to_dict().items()}
        
        vwap_series = volume_weighted_average_price(
            high=high, low=low, close=close,volume=volume,
        ).iloc[-12:]
        indicators["volume_weighted_average_price"] = {date.strftime('%Y-%m-%d'): int(value) 
                    for date, value in vwap_series.to_dict().items()}
        
        return {'stock_price': data.to_dict(orient='records'),
                'indicators': indicators}

    except Exception as e:
        return f"Error fetching price data: {str(e)}"


@tool("get_financial_metrics")
def get_financial_metrics(stock_ticker: str) -> Union[Dict, str]:
    """Fetches key financial ratios for a given stock_ticker."""
    try:
        # fetch stock infor from yahoo finance
        stock = yf.Ticker(stock_ticker)
        info = stock.info
        # return dictionary with selected metrics
        return {
            'pe_ratio': info.get('forwardPE'),
            'price_to_book': info.get('priceToBook'),
            'debt_to_equity': info.get('debtToEquity'),
            'profit_margins': info.get('profitMargins')
        }
    except Exception as e:
        return f"Error fetching ratios: {str(e)}"
  

######## SENTIMENT AGENT TOOLS ########


######## VALUATION AGENT TOOLS ########
