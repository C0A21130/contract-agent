import os
import random
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, START, END
from langfuse.callback import CallbackHandler
from typing import Literal

from components.contract_agent import ContractAgent
from components.model import State, AgentConfig
from tools.tools import get_tools

# Load environment variables from .env file
load_dotenv(verbose=True)

def route(state: State) -> Literal["fetch", "put", "thinking", "completed"]:
    """
    Route the state to the appropriate agent based on the status.
    """
    if state.status == "fetch":
        return "fetch"
    elif state.status == "put":
        return "put"
    elif state.status == "thinking":
        return "thinking"
    elif state.status == "completed":
        return "completed"
    else:
        return "completed"

def execute_agent(contract_agent: ContractAgent, handler: CallbackHandler = None):
    """
    Execute the contract agent with the given state and handler.
    """
    graph_builder = StateGraph(State)

    # Add the ContractAgent to the graph
    graph_builder.add_node("put", contract_agent.get_bind_tool_agent)
    graph_builder.add_node("fetch", contract_agent.get_bind_tool_agent)
    graph_builder.add_node("thinking", contract_agent.get_agent)
    graph_builder.add_node("completed", contract_agent.get_agent)

    # Add the thinking node to the graph
    graph_builder.add_edge(START, "thinking")
    graph_builder.add_conditional_edges("thinking", route)
    graph_builder.add_edge("fetch", "thinking")
    graph_builder.add_edge("put", "thinking")
    graph_builder.add_edge("completed", END)

    graph = graph_builder.compile()

    state = State(
        messages=[],
        board=[],
        tokens=[],
        address="",
        token_name="",
        status="thinking",
    )
    return graph.invoke(state, config={"callbacks": [handler]})

def main():

    # set model
    model = AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )

    # Set tools
    tools1 = get_tools(
        rpc_url=os.environ["RPC_URL"],
        contract_address=os.environ["CONTRACT_ADDRESS"],
        private_key=os.environ["PRIVATE_KEY"],
    )
    tools2 = get_tools(
        rpc_url=os.environ["RPC_URL"],
        contract_address=os.environ["CONTRACT_ADDRESS"],
        private_key=os.environ["SECOND_PRIVATE_KEY"],
    )
    tools3 = get_tools(
        rpc_url=os.environ["RPC_URL"],
        contract_address=os.environ["CONTRACT_ADDRESS"],
        private_key=os.environ["THIRD_PRIVATE_KEY"],
    )

    # Set handler for Langfuse
    langfuse_handler = CallbackHandler(
        secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
        host=os.environ["LANGFUSE_HOST"],
    )

    # Set Agent
    contract_agent1 = ContractAgent(
        model=model,
        config=AgentConfig(
            tools=tools1,
            name="田中",
            roll="""
                - 商店街にあるカフェの店主
                - 既存メニュー
                    - アイスコーヒー
                    - サンドイッチ
                    - チョコケーキ

                ## NFTの利用目的
                - 顧客の好みを把握するために過去のNFT取引履歴を確認する
                - 新たな料理を提案し料理の内容をNFTとして発信する
                    - NFT名に【提案】と付けてください。
                    - ドリンク系が人気であれば新たなドリンク系の料理を提案する
                    - ご飯系が人気であれば新たなご飯系の料理を提案する
            """
        ),
        handler=langfuse_handler
    )
    contract_agent2 = ContractAgent(
        model=model,
        config=AgentConfig(
            tools=tools2,
            name="山田",
            roll="""
                - カフェの新規顧客

                ## NFTの利用目的
                - まずNFTの取引履歴を確認して、どのような料理が人気かを把握する
                - もしNFTの取引履歴がない場合はお店を利用しない
                - もしお店を利用した場合NFTを発行して、感謝の気持ちや美味しかった料理のメニューを伝える
            """
        ),
        handler=langfuse_handler,
    )
    contract_agent3 = ContractAgent(
        model=model,
        config=AgentConfig(
            tools=tools3,
            name="新井",
            roll="""
                - カフェの常連客
                - よく利用するメニュー
                    - アイスコーヒー
                    - サンドイッチ
                    - チョコケーキ

                ## NFTの利用目的
                - 新しいメニューが発信されているかを過去のNFT取引履歴から確認する
                - NFTを発行してお店の良さやどのメニューがよいかを発信する
                    - 発信する内容は10文字以上20文字以内で指定する
                    - 発信するメニューはよく利用するメニューの中からランダムに一つ選ぶ
            """,
        ),
        handler=langfuse_handler,
    )

    for _ in range(10):
        try:
            random_agent = random.choice([contract_agent1, contract_agent2, contract_agent3])
            output = execute_agent(contract_agent=random_agent, handler=langfuse_handler)
            print(f"Output: {output}")
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    print(execute_agent(contract_agent=contract_agent1, handler=langfuse_handler))

if __name__ == "__main__":
    main()
