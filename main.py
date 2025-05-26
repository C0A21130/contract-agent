import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, START, END
from langfuse.callback import CallbackHandler
from typing import Literal

from components.trust_agent import TrustAgent
from components.contract_agent import ContractAgent
from components.state import State
from tools.tools import get_tools

# Load environment variables from .env file
load_dotenv(verbose=True)

# set model
model = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

# Set tools
tools = get_tools(
    rpc_url=os.environ["RPC_URL"],
    contract_address=os.environ["CONTRACT_ADDRESS"],
    private_key=os.environ["PRIVATE_KEY"],
)

# Set handler for Langfuse
langfuse_handler = CallbackHandler(
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    host=os.environ["LANGFUSE_HOST"],
)

# Set Agent
contract_agent = ContractAgent(
    model=model,
    tools=tools,
    handler=langfuse_handler,
)
trust_agent = TrustAgent(
    model=model,
)

def route(state: State) -> Literal["fetch", "put", "trust"]:
    """
    Route the state to the appropriate agent based on the status.
    """
    if state.status == "fetch":
        return "fetch"
    elif state.status == "put":
        return "put"
    else:
        return "trust"

def main():
    graph_builder = StateGraph(State)

    graph_builder.add_node("put", contract_agent.get_agent)
    graph_builder.add_node("fetch", contract_agent.get_agent)
    graph_builder.add_node("trust", trust_agent.get_agent)

    graph_builder.add_edge(START, "trust")
    graph_builder.add_conditional_edges("trust", route)
    graph_builder.add_edge("fetch", "trust")
    graph_builder.add_edge("put", END)

    graph = graph_builder.compile()

    state = State(
        messages=[],  # Initial messages
        tokens=[],  # Tokens will be populated by the agent
        address="",  # Example address
        token_name="",  # Token name will be set by the agent
        status="trust",  # Initial status
    )
    print(graph.invoke(state, config={"callbacks": [langfuse_handler]}))

if __name__ == "__main__":
    main()
