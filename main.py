import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, START, END
from langfuse.callback import CallbackHandler

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
)

trust_agent = TrustAgent(
    model=model,
)

def route(state: State):
    """
    Route the state to the appropriate agent based on the status.
    """
    if state.status == "start":
        return "put_name"
    elif state.status == "fetch":
        return "get_name"
    elif state.status == "put":
        return "put_name"
    elif state.status == "trust":
        return "eval_trust"
    elif state.status == "completed":
        return END
    else:
        raise ValueError(f"Unknown status: {state.status}")

def main():
    graph_builder = StateGraph(State)

    graph_builder.add_node("put_name", contract_agent.put_name_agent)
    graph_builder.add_node("get_name", contract_agent.get_name_agent)
    graph_builder.add_node("eval_trust", trust_agent.eval_trust_agent)

    graph_builder.add_edge(START, "get_name")
    graph_builder.add_conditional_edges("get_name", route)
    graph_builder.add_conditional_edges("eval_trust", route)
    graph_builder.add_edge("put_name", END)
    graph = graph_builder.compile()

    for event in graph.stream({"message": [{"role": "user", "content": "スマートコントラクトを呼び出してユーザー名を取得してください。もし登録されていなければユーザー名を登録してください"}]}, config={"callbacks": [langfuse_handler]}):
        for value in event.values():
            print(value)

if __name__ == "__main__":
    main()

# Example usage of the model
# <tool_name>: 選択したツールを必ず呼ぶ
# anto: いずれかのツールを呼ぶか何も呼ばない
# any: 一つの以上のツールを呼ぶ
# llm_with_tools = model.bind_tools(tools, tool_choice="auto")
# response = llm_with_tools.invoke("What is 1 + 2?")
# print(response.tool_calls)
