"""
File containing the state class implementation for the workflow graph
"""
from typing import Annotated, TypedDict
from langgraph.graph.message import AnyMessage, add_messages


# State class for the workflow
class GraphState(TypedDict):
    # list of messages seen by all LLMs
    messages: Annotated[list[AnyMessage], add_messages]

    # stock ticker (i.e. AAPL, JPM, etc.) and exchange marker (i.e., NYSE)
    stock_ticker: str
    stock_exchange: str

    # financial data regarding given stock
    stock_price_indicators: dict
    financial_metrics: dict
    financial_statements: list
    news_results: list