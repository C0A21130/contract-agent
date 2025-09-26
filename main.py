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
    # Initialize the state graph
    graph_builder = StateGraph(State)

    # Add the ContractAgent to the graph
    graph_builder.add_node("fetchTokens", contract_agent.get_agent)
    graph_builder.add_node("putToken", contract_agent.get_agent)
    graph_builder.add_node("reporting", contract_agent.get_agent)

    # Add the thinking node to the graph
    graph_builder.add_edge(START, "fetchTokens")
    graph_builder.add_conditional_edges("fetchTokens", contract_agent.route)
    graph_builder.add_edge("putToken", "reporting")
    graph_builder.add_edge("reporting", END)

    # Compile the graph
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
            roll="私はソフトウェアエンジニアです．他のユーザーからの貢献に対してNFTを送信して貢献を評価します．"
        ),
        handler=langfuse_handler
    )

    state = State(
        messages=[],
        tokens=[],
        address="",
        token_name="",
        status="fetchTokens"
    )
    graph = build_agent_graph(contract_agent=contract_agent)
    streams = graph.stream(state, config={"callbacks": [langfuse_handler]})
    result = None
    for stream in streams:
        result = stream
        print(stream)
    print("result:", result)

if __name__ == "__main__":
    main()
