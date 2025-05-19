import json
from typing import List, Literal
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate

from components.state import State

class ContractAgent:

    def __init__(self, model, tools: List):
        self.model = model
        self.tools = tools

    def put_name_agent(self, state: State):

        # Define the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    """
                    与えられたinputに従ってスマートコントラクトを呼び出してください
                    """,
                ),
                ("placeholder", "{messages}"),
            ]
        )

        # Create Agent
        agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            state_modifier=prompt,
        )

        output = agent.invoke(
            {"messages": [f"スマートコントラクトを呼び出して、名前を設定してください。設定する名前は{state.name}です。"]},
        )

        return {"messages": [output["messages"]], "status": "completed"}

    def get_name_agent(self, state: State):
        class OutputJson(BaseModel):
            messages: List[str] = Field(..., description="messages")
            status: Literal["trust", "completed"] = Field(..., description="スマートコントラクトを呼び出して、状態を取得した結果。呼び出して値が取得できたらcompleted、取得できなかったらtrustとする。")

        # Define the output parser
        output_parser = PydanticOutputParser(pydantic_object=OutputJson)
        format_instructions = output_parser.get_format_instructions()

        # Define the prompt
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    """
                    与えられたinputに従ってスマートコントラクトを呼び出してください

                    {format_instructions}
                    """,
                ),
                ("placeholder", "{messages}"),
            ]
        )
        prompt = prompt_template.partial(
            format_instructions=format_instructions
        )

        # Create the agent
        agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            state_modifier=prompt,
        )

        output = agent.invoke(
            {"messages": ["スマートコントラクトを呼び出して、名前を取得してください。"]}
        )
        status = json.loads(output["messages"][-1].content)["status"]

        return {"message": [output["messages"]], "status": status}
