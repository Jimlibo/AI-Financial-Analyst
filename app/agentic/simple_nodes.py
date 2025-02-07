"""
File containing tool functions for the different agents in the graph.
"""
import os
import pandas as pd
import datetime as dt
import yfinance as yf

from typing import TypedDict

from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD
from ta.volume import volume_weighted_average_price

from app.agentic.utils import extract_text_from_url

import serpapi
from dotenv import load_dotenv
load_dotenv()


def get_stock_prices(state: TypedDict) -> TypedDict: # type:ignore
    """Fetches historical stock price data and technical indicator for a given stock_ticker."""
    try:
        # get stock data from yahoo finance and store them in a dataframe
        data = yf.download(
            state['stock_ticker'],
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
        
        return {
            'stock_price_indicators': {
                'stock_price': data.to_dict(orient='records'),
                'indicators': indicators
            }
        }

    except Exception as e:
        return {"stock_price_indicators": {}}


def get_financial_metrics(state: TypedDict) -> TypedDict: # type:ignore
    """Fetches key financial ratios for a given stock_ticker."""
    try:
        # fetch stock infor from yahoo finance
        stock = yf.Ticker(state['stock_ticker'])
        info = stock.info
        # return dictionary with selected metrics
        return {
            'financial_metrics': {
                'pe_ratio': info.get('forwardPE'),
                'price_to_book': info.get('priceToBook'),
                'debt_to_equity': info.get('debtToEquity'),
                'profit_margins': info.get('profitMargins')
            }
        }
    except Exception as e:
        return {"financial_metrics": {}}


def get_general_financial_info(state: TypedDict) -> TypedDict: # type:ignore
    """
    Fetches general financial information for the given stock, including the three main
    financial statements (Income Statement, Balance Sheet and Cash flow Statement) as well 
    as articles, 
    """
    try:
        # set up query parameters
        params = {
        "engine": "google_finance",
        "q": f"{state['stock_ticker']}:{state['stock_exchange']}",
        "api_key": os.getenv("SERPAPI_KEY_TOKEN")
        }

        # fetch results as a dictionary
        results = serpapi.search(params).as_dict()

        # extract articles from fetched results
        articles = []
        if results.get('news_results', False):
            articles = []
            # set an upper limit in the number of fetched articles
            limit = min(len(state['news_results']), 5)
            for item in state['news_results'][:limit]:
                # if item contains nested articles, pick the first of those artickles
                if item.get("items", False):
                    # append the title and link of the article
                    articles.append((item['items'][0]['snippet'], item['items'][0]['link']))
                # else, add the article to the list
                else:
                    articles.append(item['snippet'], item['link'])

        # add financial statements and related articles (if they exist) to the graph state
        return {
            "financial_statements": results.get('financials', []),
            "news_results": articles
        }
    
    except Exception as e:
        return {
            "financial_statements": [],
            "news_results": []
        }


def combine_stock_data(state: TypedDict) -> TypedDict: # type:ignore
    """
    Combines price data, indicators, financial metrics, financial statements
    and relevant articles for a stock.
    """
    # convert relevant articles links to text if they exist
    if state.get('news_results', False):
        # convert links to text
        articles = list(map(lambda x: extract_text_from_url(x), state['news_results']))
        # update apporpriate state attribute
        return {"news_results": articles}
    # else, do not change anything from the state attributes
    return {}
