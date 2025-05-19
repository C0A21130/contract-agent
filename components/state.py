from typing import Annotated, List, Literal
from pydantic import BaseModel
from langgraph.graph.message import add_messages

class State(BaseModel):
    """
    State for the state machine.
    """
    message: Annotated[List[str], add_messages]
    name: str
    status: Literal["start", "fetch", "put", "trust", "completed"] = "start"
