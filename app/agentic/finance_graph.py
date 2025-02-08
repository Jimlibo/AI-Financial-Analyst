"""
File containing class implementation of the workflow graph.
"""
import os
import json
import argparse

from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langgraph.graph import StateGraph, START, END

from states.graph_state import GraphState
from nodes.llm_node import LLMNode
from utils.prompts import (
    TECHNICAL_ANALYSIS_PROMPT, 
    SENTIMENT_ANALYSIS_PROMPT, 
    VALUATION_ANALYSIS_PROMPT,
    REPORT_WRITING_PROMPT
)
from nodes.simple_nodes import (
    get_stock_prices, 
    get_financial_metrics, 
    get_general_financial_info,
    combine_stock_data
)

from dotenv import load_dotenv
load_dotenv()


class FinanceGraph():
    """
    Class that builds, compiles and runs a workflow that produces a detailed
    report regarding a given stock. The report features price data, financial
    metrics and indicators as well as relevant articles.
    """
    def __init__(self, hf_model: str | None=None):
        # initialize LLM from Huggingface
        hf_endpoint = HuggingFaceEndpoint(
            repo_id=hf_model if hf_model is not None else "Qwen/Qwen2.5-72B-Instruct",
            task="text-generation",
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
        )
        self.llm = ChatHuggingFace(llm=hf_endpoint)
        self.graph = None

    def build(self):
        """
        Build and compile the graph.
        """
        builder = StateGraph(GraphState)
        # add simple nodes
        builder.add_node("get_stock_prices", get_stock_prices)
        builder.add_node("get_financial_metrics", get_financial_metrics)
        builder.add_node("get_general_financial_info", get_general_financial_info)
        builder.add_node("combine_stock_data", combine_stock_data)

        # add LLM nodes
        builder.add_node("technical_analysis", LLMNode(self.llm, TECHNICAL_ANALYSIS_PROMPT))
        builder.add_node("sentiment_analysis", LLMNode(self.llm, SENTIMENT_ANALYSIS_PROMPT))
        builder.add_node("valuation_analysis", LLMNode(self.llm, VALUATION_ANALYSIS_PROMPT))
        builder.add_node("report_writer", LLMNode(self.llm, REPORT_WRITING_PROMPT))

        # add edges
        builder.add_edge(START, "get_stock_prices")
        builder.add_edge(START, "get_financial_metrics")
        builder.add_edge(START, "get_general_financial_info")

        builder.add_edge("get_stock_prices", "combine_stock_data")
        builder.add_edge("get_financial_metrics", "combine_stock_data")
        builder.add_edge("get_general_financial_info", "combine_stock_data")

        builder.add_edge("combine_stock_data", "technical_analysis")
        builder.add_edge("combine_stock_data", "sentiment_analysis")
        builder.add_edge("combine_stock_data", "valuation_analysis")

        builder.add_edge("technical_analysis", "report_writer")
        builder.add_edge("sentiment_analysis", "report_writer")
        builder.add_edge("valuation_analysis", "report_writer")

        builder.add_edge("report_writer", END)

        # Compile graph
        self.graph = builder.compile()

    def run(self):
        pass
