"""
File containing class implementation of the workflow graph.
"""
import os
import json
import argparse
from rich.console import Console
from typing import Literal

from langgraph.graph import StateGraph, START, END

from states.graph_state import GraphState
from nodes.llm_node import LLMNode
from utils.utils import llm_endpoint
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

console = Console()


class FinanceGraph():
    """
    Class that builds, compiles and runs a workflow that produces a detailed
    report regarding a given stock. The report features price data, financial
    metrics and indicators as well as relevant articles.
    """
    def __init__(self, type: Literal["hugging-face", "ollama", "llama-cpp"]="hugging-face",
                model_name: str | None=None, url: str | None=None, model_path: str | None=None,
                config_file: str | None=None):
        # first option: use a configuration file for llm initialization
        if config_file is not None:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                raise FileNotFoundError(f"File '{config_file}' does not exist!")
        
        # second option: get the necessary configuration from parameters
        else:
            # construct the configuration using defaults when argument is not specified
            config = {
                "model_path": model_path if model_path is not None else ""
            }
            if model_name is not None:
                config["model_name"] = model_name
            if url is not None:
                config["url"] = url

        self.llm = llm_endpoint(type=type, config=config)
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

    def run(self, stock_ticker: str, stock_exchange: str, dest_dir: str | None=None) -> tuple[str, int]:
        """
        Take as input a stock ticker and the stock exchange market and return
        a detailed financial report regarding the stock.

        If parameter `dest_dir` is specified, saves the fetched data in the given directory.
        """
        try:
            final_state = self.graph.invoke({
                "messages": [],
                "stock_ticker": stock_ticker,
                "stock_exchange": stock_exchange
            })
            
            if dest_dir is not None:
                # create destination directory if it does not already exist
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)

                # get all dictionary-like attributes of graph state and save them in a list as tuple (attr_name, attr_value)
                json_files = [(attr, final_state[attr]) for attr in final_state if type(attr) == dict]
                # store each of those attributes in its own .json file inside dest_dir
                for name, content in json_files:
                    with open(os.path.join(dest_dir, f"{name}.json"), 'w') as f:
                        json.dump(content, f)
                
                # save LLM response contents in .txt files
                for msg in final_state['messages']:
                    with open(os.path.join(dest_dir, f"{msg.name}.txt"), 'w') as f:
                        f.write(msg.content)

            # if everything went smoothly, return final report and 1 to represent 'OK' code
            return final_state["messages"][-1].content, 1

        except Exception as e:
            raise e
            # if error occured, return the error message along with 0 for 'Failed' code
            return f"[ERROR]: {str(e)}", 0


def parse_input():
    parser = argparse.ArgumentParser(prog="FinanceGraph")
    parser.add_argument(
        "--serving-type",
        action="store",
        dest="serving_type",
        choices=["ollama", "hugging-face", "llama-cpp"],
        required=True,
        help="LLM serving method",
    )
    parser.add_argument(
        "-m",
        "--model-name",
        action="store",
        dest="model_name",
        required=False,
        help="LLM that will be used (when using llama.cpp for model serving, this argument is ignored)",
    )
    parser.add_argument(
        "--model-path",
        action="store",
        dest="model_path",
        required=False,
        help="Path of the llama.cpp model file (specify only when using llama.cpp for model serving)",
    )
    parser.add_argument(
        "--url",
        action="store",
        dest="url",
        required=False,
        help="Ollama ulr (specify only when using Ollama for model serving)",
    )
    parser.add_argument(
        "-c",
        "--config-file",
        action="store",
        dest="config_file",
        required=False,
        help="Configuration (.json) file  with the necessary initialization arguments of LLM interface",
    )
    parser.add_argument(
        "-s",
        "--stock",
        action="store",
        dest="stock",
        required=True,
        help="The ticker of the desired stock (i.e. AAPL, GOOG, etc.)",
    )
    parser.add_argument(
        "-e",
        "--exchange",
        action="store",
        dest="exchange",
        required=True,
        help="The exchange market of the stock (i.e. NASDAQ, NYSE, etc.)",
    )
    parser.add_argument(
        "-d",
        "--dest-dir",
        action="store",
        required=False,
        help="Destination directory to which the fetched data will be stored (if not specified, data won't be stored)"
    )
    return parser.parse_args()


def main(args):
    # initialize and compile the finance graph
    # try:
    fg = FinanceGraph(
        type=args.serving_type,
        model_name=args.model_name, 
        url=args.url, 
        model_path=args.model_path,
        config_file=args.config_file
    )
    fg.build()
    
    with console.status("[cyan]Generating report..."):
        response, success = fg.run(stock_ticker=args.stock, stock_exchange=args.exchange, dest_dir=args.dest_dir)

    # if no error occured, return financial report along with success message in green color
    if success:
        console.print("[green bold]Report Generated Successfully!")
        print(response)
    else:
        # if error occurred, return the error message in bold red color
        console.print(f"[red bold]{response}")
    # except Exception as e:
        # console.print(f"[red bold][ERROR]:{e}")

if __name__ == "__main__":
    ARGS = parse_input()
    main(ARGS)
