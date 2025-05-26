from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from components.state import State

class OutputJson(BaseModel):
    messages: str = Field(..., description="取引の内容や判断した理由や過程についても説明してください。")
    address: str = Field(..., description="NFT(Non-Fungible Token)を発行して転送するユーザーのウォレットアドレスを示す。ユーザーのアドレスは、アドレス一覧から選択される。")
    token_name: str = Field(..., description="考案したトークンの名前。どのような贈与の内容を表すかを示す。")
    status: Literal["fetch", "put", "completed"] = Field(..., description="情報が不足している場合はfetch、情報が十分であればputとする。")

class TrustAgent:
    def __init__(self, model, handler=None):
        self.model = model
        self.config = {"callbacks": [handler]}

    def get_agent(self, state: State):

        # Define the output parser
        output_parser = PydanticOutputParser(pydantic_object=OutputJson)
        format_instructions = output_parser.get_format_instructions()

        # Define the prompt
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    # Trust Agent

                    ## 概要
                    あなたは、NFT(Non-Fungible Token)を発行して転送する考案するエージェントです。
                    ユーザーのウォレットアドレスを信用度に基づいて選択し、贈与の内容(Token Name)を考案します。
                    もし過去の取引情報一覧がない場合は、ユーザーの信用度を評価するための情報を収集し、取引相手を選択します。

                    ### 用語
                    - 信用スコア：取引相手に関する信用度を定量化したスコアです。このスコアは過去の取引履歴から算出されます。過去の取引数が多く、そのコミュニティにおける評判が高い値となります。
                    - 一般的信頼：相手についての情報が少ない場合の相手の信頼性に対するデフォルト値。このデフォルト値の高低差によって高信頼者と低信頼者に分けることが可能です。
                        - 高信頼者：他者の人間性を正確に推定できる人
                        - 低信頼者：人間性を見抜く社会的知性に欠けた人

                    ### 取引相手の選択
                    過去の取引相手に基づいて選択されます。
                    信用度は、過去の取引履歴やユーザーの特徴を元に評価されます。

                    ## 目的
                    各エージェントを呼び出して、ユーザーのウォレットアドレスと贈与の内容(Token Name)を考案し、スマートコントラクトを呼び出してNFTを発行します。
                    ユーザーの信用度に基づいて、取引相手を選択し、贈与の内容を考案します。
                    もし過去の取引情報がない場合は情報を収集し、取引相手を選択します。
                    
                    ### 各エージェントの役割
                    以下が各エージェントの役割です。
                    - contract_agent: ユーザーのウォレットアドレスと贈与の内容(Token Name)を考案し、スマートコントラクトを呼び出してNFTを発行します。
                    - trust_agent: contract_agentの呼び出して取得した結果からユーザーのウォレットアドレスと贈与の内容(Token Name)を考案します。

                    ## 手順
                    1. スマートコントラクトを呼び出して、過去の取引履歴を取得します。
                    2. 過去の取引履歴から、ユーザーの信用度を評価します。
                    3. ユーザーの信用度を考慮して、取引相手のウォレットアドレスと贈与の内容(Token Name)を選択します。
                    4. スマートコントラクトを呼び出して、NFTを発行します。

                    ## 過去の取引情報一覧
                    {transactions}

                    ### 各トークンの項目
                    - From address：発行主のウォレットアドレス
                    - To address：送信先ウォレットアドレス
                    - Token Name：どのような贈与の内容を表すかを示します。

                    ## 出力形式
                    あなたは、以下のJSON形式で出力を返してください。

                    {format_instructions}
                    """
                ),
                (
                    "human",
                    """
                    {input}
                    """
                )
            ]
        )
        prompt = prompt_template.partial(format_instructions=format_instructions)
        transactions = "情報はありません" if len(state.tokens) == 0 else "\n".join(
            f"""
                token {token.token_id}:
                - From address: {token.from_address}
                - To address: {token.to_address}
                - Token name: {token.token_name}
            """ for token in state.tokens
        )

        agent = prompt | self.model | output_parser

        # Get the user input
        if self.config["callbacks"][0] == None:
            output = agent.invoke(
                {"input": "贈与をしてください", "transactions": transactions}
            )
        else:
            output = agent.invoke(
                {"input": "論文を探してくれてありがとう", "transactions": transactions},
                config=self.config
            )
        message = output.messages
        tokens = state.tokens
        address = output.address
        token_name = output.token_name
        status = output.status

        return {
            "messages": message,
            "tokens": tokens,
            "address": address,
            "token_name": token_name,
            "status": status
        }
