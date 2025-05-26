from typing import List
from langchain_core.prompts import ChatPromptTemplate

from components.state import State

class ContractAgent:

    def __init__(self, model, tools: List):
        self.model = model
        self.tools = tools

    def get_agent(self, state: State):
        
        # Define the prompt
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    """
                    与えられたinputに従ってスマートコントラクトを呼び出してください
                    """,
                ),
                ("human", "{input}"),
            ]
        )
        if(state.status == "put"):
            human_input = f"""
                スマートコントラクトを呼び出して、NFT(Non-Fungible Token)を発行してください。
                以下の情報を含めてください:
                - トークンの名前: {state.token_name}
                - トークンの所有者のアドレス: {state.address}
            """
        elif(state.status == "fetch"):
            human_input = f"スマートコントラクトを呼び出して、過去のNFT(Non-Fungible Token)の取引履歴を取得してください。address: {state.address}"
        prompt = prompt_template.format_messages(
            input=human_input
        )

        # execute the model with tools
        model_with_tool = self.model.bind_tools(self.tools)
        output = model_with_tool.invoke(prompt)
        
        # extract tool calls from the output
        if not output.tool_calls:
            return {"messages": "No tool calls were made.", "status": "trust"}
        else:
            for tool_call in output.tool_calls:
                if tool_call["name"] == "put_token":
                    token_id = self.tools[2].invoke(tool_call["args"])
                    message = f"NFTが発行されました。トークンID: {token_id}"
                    tokens = state.tokens
                elif tool_call["name"] == "fetch_tokens":
                    tokens = self.tools[3].invoke(tool_call["args"])
                    message = f"取引履歴が取得されました。トークンの数: {len(tokens)}"
        
        return {"messages": message, "tokens": tokens, "address": state.address, "token_name": state.token_name, "status": "trust"}
