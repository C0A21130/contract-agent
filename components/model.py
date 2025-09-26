from typing import Annotated, List, Literal
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class Token(BaseModel):
    """
    Token class to represent a token in the state machine.
    """
    from_address: str
    to_address: str
    token_id: int
    token_name: str

class AgentConfig(BaseModel):
    """
    Configuration for the agent.
    """
    tools: List
    name: str
    roll: str

class State(BaseModel):
    """
    State for the state machine.
    """
    messages: Annotated[List[BaseMessage], add_messages] = []
    tokens: List[Token] = []
    address: str = ""
    token_name: str = ""
    status: Literal["fetchTokens", "putToken", "reporting", "__end__"] = "fetchTokens"
