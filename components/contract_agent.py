from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import PydanticOutputParser

from components.model import State, AgentConfig, OutputJson

class ContractAgent:

    def __init__(self, model, config: AgentConfig, handler=None):
        self.model = model
        self.tools = config.tools
        self.name = config.name
        self.roll = config.roll

        # Set up the callback handler
        if handler is None:
            self.config = {"callbacks": [None]}
        else:
            self.config = {"callbacks": [handler]}
        
    def get_agent(self, state: State) -> State:
        # Define the output parser
        output_parser = PydanticOutputParser(pydantic_object=OutputJson)
        format_instructions = output_parser.get_format_instructions()
        
        # Define the prompt
        prompt = ChatPromptTemplate.from_messages([
            (
                'system',
                """
                # スマートコントラクトエージェント
                あなたはスマートコントラクトエージェントとしてユーザーをサポートします。

                ## 出力形式
                {format_instructions}
                """,
            ),
            (
                "user",
                """
                # ユーザーの情報
                - 自分のユーザー名：{name}
                {roll}

                ## 相手ユーザーの情報
                - 田中
                    - 商店街にあるカフェの店主
                    - アドレス: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
                - 山田
                    - 商店街を利用する顧客
                    - アドレス: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
                - 新井
                    - 商店街を利用する顧客, カフェの常連客
                    - アドレス: 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC

                ## ユーザーの役割
                {roll}

                ## 行動
                {input}
                """
            )
        ])
        if(state.status == "thinking"):
            token_details = "NFTを発行しないならばfetchにして過去のNFTの取引履歴を取得する"
            if state.tokens:
                token_details = "\n".join(
                    f"- トークンID: {token.token_id}, トークン名: {token.token_name}, 転送元アドレス: {token.from_address}, 転送先アドレス: {token.to_address}"
                    for token in state.tokens
                )
            input_word = f"""
                現在の状態とアクション一覧を考慮して次のアクションを決める
                
                - もしNFTを発行する目的があれば次のアクションをputにする
                - 現在発行されているNFTを確認したい場合、次のアクションはfetchにする

                ## 現在発行されているNFT
                {token_details}

                ## アクション一覧
                - put: 情報の発信や感謝を伝えるために発行するNFTの名前と転送先アドレスを指定してスマートコントラクトを呼び出す
                - fetch: スマートコントラクトを呼び出して過去のNFTの取引履歴を取得する
            """
        else:
            input_word = f"""
                次のアクションをcompletedにして行動を終了してください。
            """

        # execute the model with not tools
        output: State = None
        agent = prompt | self.model | output_parser
        if self.config["callbacks"][0] == None:
            output = agent.invoke({
                "name": self.name,
                "roll": self.roll,
                "input": input_word,
                "format_instructions": format_instructions
            })
        else:
            output = agent.invoke({
                "name": self.name,
                "roll": self.roll,
                "input": input_word,
                "format_instructions": format_instructions
            },config=self.config)

        # Return the state with updated messages and status
        return State(
            messages=[HumanMessage(content=output.message)],
            tokens=state.tokens,
            address=output.address if hasattr(output, 'address') else state.address,
            token_name=output.token_name if hasattr(output, 'token_name') else state.token_name,
            status=output.status if hasattr(output, 'status') else state.status,
        )

    def get_bind_tool_agent(self, state: State) -> State:
        new_status = "completed"
        message = "アクション完了"
        input_word = ""
        tokens = []
        token_id = ""

        # Define the prompt
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    """
                    # スマートコントラクトエージェント
                    あなたはスマートコントラクトエージェントとしてユーザーをサポートします。
                    """,
                ),
                (
                    "user",
                    """
                    # ユーザーの情報
                    - ユーザーの名前：{name}

                    # 行動
                    {input}
                    """
                )
            ]
        )

        if(state.status == "put"):
            input_word = f"""
                スマートコントラクトを呼び出して情報を基にNFTを発行してください。

                ## 情報
                - 発行するNFTの情報: {state.token_name}
                - 送信先のNFTアドレス: {state.address}
            """
        elif(state.status == "fetch"):
            input_word = f"""
                スマートコントラクトを呼び出して、過去のNFTの取引履歴を取得してください。
                - アドレス: 0x0000000000000000000000000000000000000000
            """
        prompt = prompt_template.format_messages(
            name=self.name,
            input=input_word
        )

        # execute the model with tools
        model_with_tool = self.model.bind_tools(self.tools)

        # Invoke the model with the prompt
        if self.config["callbacks"][0] == None:
            output = model_with_tool.invoke(prompt)
        else:
            output = model_with_tool.invoke(prompt, config=self.config)

        # Process tool calls
        for tool_call in output.tool_calls:
            if tool_call["name"] == "put_token":
                token_id = self.tools[0].invoke(tool_call["args"])
                message = f"NFTが発行されました。トークンID: {token_id}"
                new_status = "completed"
            elif tool_call["name"] == "fetch_tokens":
                tokens = self.tools[1].invoke(tool_call["args"])
                message = f"取引履歴が取得されました。トークンの数: {len(tokens)}"
                new_status = "thinking"
        return {
            "messages": [HumanMessage(content=message)],
            "tokens": tokens,
            "address": state.address,
            "token_name": state.token_name,
            "status": new_status,
        }
