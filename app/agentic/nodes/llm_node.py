"""
File containing class implementation for nodes that perform LLM calls
"""
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate

from states.graph_state import GraphState


class LLMNode:
    """
    Class implementation for graph nodes that use LLMs
    """
    def __init__(self, runnable: Runnable, prompt: ChatPromptTemplate, name: str | None=None):
        self.llm = prompt | runnable
        self.name = "llm_node" if name is None else name

    def __call__(self, state: GraphState, config: RunnableConfig | None=None) -> dict:
        """
        Make LLM call based on input state and update the state messages list with the 
        response.
        """
        # get the response from the LLM
        response = self.llm.invoke(state)

        # handle different types of responses
        if type(response) == str:
            return {"messages": [AIMessage(content=response)]}
        else:
            return {"messages": response}
