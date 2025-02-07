"""
File containing class implementation of the workflow graph.
"""
import os
import json
import argparse

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from app.agentic.states.graph_state import GraphState
from app.agentic.nodes.llm_node import LLMNode
from app.agentic.utils.prompts import (
    TECHNICAL_ANALYSIS_PROMPT, 
    SENTIMENT_ANALYSIS_PROMPT, 
    VALUATION_ANALYSIS_PROMPT,
    REPORT_WRITING_PROMPT
)
from app.agentic.nodes.simple_nodes import (
    get_stock_prices, 
    get_financial_metrics, 
    get_general_financial_info
)

class FinanceGraph():
    """
    Class that builds, compiles and runs a workflow that produces a detailed
    report regarding a given stock. The report features price data, financial
    metrics and indicators as well as relevant articles.
    """
    def __init__(self):
        pass

    def build(self):
        pass

    def run(self):
        pass

    def build_and_run(self):
        pass