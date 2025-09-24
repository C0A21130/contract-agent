import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, START, END
from langfuse.callback import CallbackHandler

from components.contract_agent import ContractAgent
from components.model import State, AgentConfig
from tools.tools import get_tools

load_dotenv(verbose=True)

def build_agent_graph(contract_agent: ContractAgent):
    """
    Build the agent graph with the ContractAgent.
    """
    graph_builder = StateGraph(State)

    # Add the ContractAgent to the graph
    graph_builder.add_node("put", contract_agent.get_bind_tool_agent)
    graph_builder.add_node("fetch", contract_agent.get_bind_tool_agent)
    graph_builder.add_node("thinking", contract_agent.get_agent)
    graph_builder.add_node("completed", contract_agent.get_agent)

    # Add the thinking node to the graph
    graph_builder.add_edge(START, "thinking")
    graph_builder.add_conditional_edges("thinking", contract_agent.route)
    graph_builder.add_edge("fetch", "thinking")
    graph_builder.add_edge("put", "thinking")
    graph_builder.add_edge("completed", END)

    graph = graph_builder.compile()
    return graph

def main():

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
        config=AgentConfig(
            tools=tools,
            name="田中",
            roll="""
            """
        ),
        handler=langfuse_handler
    )

    state = State(
        messages=[],
        board=[],
        tokens=[],
        address="",
        token_name="",
        status="thinking",
    )
    graph = build_agent_graph(contract_agent=contract_agent)
    streams = graph.stream(state, config={"callbacks": [langfuse_handler]})
    for stream in streams:
        print(stream)

if __name__ == "__main__":
    main()
