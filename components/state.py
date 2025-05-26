from typing import Annotated, List, Literal
from pydantic import BaseModel
from langgraph.graph.message import add_messages

class Token(BaseModel):
    # This class is used to represent a token.
    from_address: str
    to_address: str
    token_id: int
    token_name: str

class State(BaseModel):
    """
    State for the state machine.
    """
    messages: Annotated[List[str], add_messages] = []
    tokens: List[Token] = []
    address: str = ""
    token_name: str = ""
    status: Literal["start", "fetch", "put", "trust", "completed"] = "start"
