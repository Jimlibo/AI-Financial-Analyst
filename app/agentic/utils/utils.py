"""
File containing utility functions.
"""
import os
from typing import Literal

from langchain_ollama import ChatOllama
from langchain_community.chat_models import ChatLlamaCpp
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from urllib.request import urlopen
from bs4 import BeautifulSoup


def extract_text_from_url(url: str) -> str:
    """
    Extracts text from a given url and returns it
    in a human-readable format.
    """
    try:
        # get the html content from the url
        html = urlopen(url).read()
        # parse the html using bs4
        soup = BeautifulSoup(html, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract() 

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # drop blank lines and form the final extracted text
        text = '\n'.join(line for line in lines if line)
        return text
    except:
        return ""
    

def llm_endpoint(type: Literal["hugging-face", "ollama", "llama-cpp"], config: dict = {}) -> BaseChatModel:
    """
    Returns a ChatModel using the given serving type and configuration.
    """
    if type == "hugging-face":
        api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
        if not api_key:
            raise KeyError("You do not have a hugging-face api key!")
        # return  LLM from Huggingface
        hf_endpoint = HuggingFaceEndpoint(
            repo_id=config.get("model_name", "Qwen/Qwen2.5-72B-Instruct"),
            task="text-generation",
            huggingfacehub_api_token=api_key
        )
        return ChatHuggingFace(llm=hf_endpoint)

    elif type == "ollama":
        # ensure that model name is provided
        if not config.get("model_name", ""):
            raise KeyError("Ollama model name is not provided!")
        # return LLM from ollama
        return ChatOllama(
            # if no ollama url is specified, use localhost with the default Ollama port
            base_url=config.get("url", "http://127.0.0.1:11434"),
            model=config["model_name"],
            temperature=0.1,
            num_predict=-2,
        )
    
    elif type == "llama-cpp":
        # ensure that model path is given and it exists
        model_path = config.get("model_path", "")
        if not model_path:
            raise KeyError("Llama.cpp model path is not provided!")
        elif model_path and not os.path.exists(model_path):
            raise FileNotFoundError(f"File '{model_path}' does not exist!")
        # return LLM from llama.cpp
        return ChatLlamaCpp(
            temperature=0.5,
            model_path=model_path,
            n_ctx=10000,
            max_tokens=512,
            repeat_penalty=1.5,
            top_p=0.5
        )
            
    else:
        raise ValueError(f"Type '{type}' is not supported!")