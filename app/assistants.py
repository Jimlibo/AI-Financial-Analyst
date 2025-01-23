"""
File containing assistant class implementations for the agent nodes of the graph
"""
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.prompts import ChatPromptTemplate

from langgraph.prebuilt import tools_condition
from langgraph.graph import END

from app.agentic.states import AgentState


class GeneralAssistant:
    """
    Base class implementation for different agents
    """
    def __init__(self, runnable: Runnable, prompt: ChatPromptTemplate, name: str | None=None):
        self.runnable = runnable
        self.name = "agent" if name is None else name

    def __call__(self, state: AgentState, config: RunnableConfig) -> dict:
        while True:
            result = self.runnable.invoke(state)

            # check that llm response is not empty - add correction message if it is
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}
    
    def route_assistant(self, state: AgentState) -> str:
        """
        Decide which node should be next, based on the last message of the state.
        """
        route = tools_condition(state)    
        return END if route == END else f"{self.name}_tools"
    

class SpecializedAssistant(GeneralAssistant):
    """
    Class that implements secondary agents, each specialized in a specific task such as sentiment analysis,
    technical analysis, stock indicator computation, etc. Each specialized agent can either call one of his
    tools or continue to the risk manager agent.
    """
    def route_assistant(self, state:AgentState) -> str:
        """
        Decide which node should be next, based on the last message of the state.
        """
        # if last message contained a tool call, go to the appropriate tool
        if state["messages"][-1].tool_calls:
            return f"{self.name}_tools"

        # else, continue to the risk manager agent
        return "risk_manager"
        
        
