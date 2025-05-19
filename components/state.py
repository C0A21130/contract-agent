from typing import Annotated, List, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages

class State(BaseModel):
    """
    State for the state machine.
    """
    messages: Annotated[List[str], add_messages] = []
    name: str = ""
    status: Literal["start", "fetch", "put", "trust", "completed"] = "start"
