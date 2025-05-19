from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from components.state import State

class TrustAgent:
    def __init__(self, model):
        self.model = model

    def eval_trust(self, state: State):

        class OutputJson(BaseModel):
            messages: List[str] = Field(..., description="messages")
            name: str = Field(..., description="")
            status: Literal["fetch", "put"] = Field(..., description="情報が不足している場合はfetch、情報が十分であればputとする。")

        # Define the output parser
        output_parser = PydanticOutputParser(pydantic_object=OutputJson)
        format_instructions = output_parser.get_format_instructions()

        prompt_template = ChatPromptTemplate(
            [
                (
                    "system",
                    """
                    スマートコントラクトを呼び出して名前を設定することができたかどうか確認してください。

                    {format_instructions}
                    """
                ),
                (
                    "human",
                    """
                    登録する日本人の名前を考えてください。
                    考えることがができなければ、情報が不足しているのでstatusをfetchにしてください。
                    もしできていれば、情報は十分なのでstatusをputにしてください。
                    """,
                )
            ]
        )
        prompt = prompt_template.partial(format_instructions=format_instructions)

        agent = prompt | self.model | output_parser

        # Get the user input
        output = agent.invoke(
            {"input": ""},
        )
        message = output.messages
        name = output.name
        status = output.status

        return {"message": [message], "name": name, "status": status}
