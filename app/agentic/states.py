"""
File containing the state class implementation for the stateful graph
"""
from typing import Annotated, TypedDict
from langgraph.graph.message import AnyMessage, add_messages


# State class for the workflow
class AgentState(TypedDict):
    # list of messages seen by all agents so that they have access to previous outputs
    messages: Annotated[list[AnyMessage], add_messages]
    stock_name: str