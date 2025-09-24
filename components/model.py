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
    status: Literal["fetch", "put", "thinking", "completed"] = "thinking"

class OutputJson(BaseModel):
    message: str = Field(..., description="取引の内容や判断した理由や過程についても説明してください。")
    address: str = Field(..., description="NFTを発行して転送するユーザーのウォレットアドレスを示す。ユーザーのアドレスは、アドレス一覧から選択される。")
    token_name: str = Field(..., description="提案する料理名やおすすめの料理名、感謝などを示す。判断した理由や過程についても示してください。")
    status: Literal["fetch", "put", "completed"] = Field(..., description="NFT取引情報が不足している場合はfetch、情報が十分であればputとする。終了する場合はcompletedとする。")
