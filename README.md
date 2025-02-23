# AI-Financial-Analyst

![Python](https://img.shields.io/badge/python-v3.12-blue.svg)
![LangChain](https://img.shields.io/badge/langchain-v0.3.22-orange.svg)
![Langgrap](https://img.shields.io/badge/langgraph-v0.2.56-yellow.svg)

## General
Get a detailed report for a specific stock from a specific exchange, by leveraging the power of LLMs and langgraph.

## Future Steps
- [ ] add support for different LLM servings
    - [ ] add support for Ollama
    - [ ] add support for llama.cpp
- [ ] add UI
    - [ ] add home page where stock and exchange are specified
    - [ ] add visualization pages with graphs regarding fetched data

## Setup
In order to run this repo, first clone it using the following command:
```bash
git clone https://github.com/Jimlibo/AI-Financial-Analyst.git
```
After you have cloned the repository, navigate to the repository and install necessary python packages:
```bash
cd AI-Financial-Analyst
pip install -r app/requirements.txt
```

## Run from the CLI
After installing all necessary packages, you can get a detailed financial report for your desired stock, by running the 
command:
```bash
python app/agentic/finance_graph.py --stock <your stock> --exchange <exchange market of the stock>
```

In the previous command, you can specify three possible CLI parameters:
* <b>--stock</b>: the stock ticker (i.e. AAPL, GOOGL, JPM, etc.)
* <b>--exchange</b>: the market where the stock is exchanged (i.e. NYSE, NASDAQ, etc.)
* <b>[--dest-dir]</b>: an optional parameter, specifying the directory where fetched data will be stored

For example, to get a financial report on Apple's stock you have to run the following:
```bash
python app/agentic/finance_graph.py --stock AAPL --exchange NASDAQ --dest-dir ~/apple_stock_data
```


## License
Distributed under the Apache License. See 
[LICENSE](https://github.com/Jimlibo/AI-Financial-Analyst/blob/main/LICENSE) for more information.