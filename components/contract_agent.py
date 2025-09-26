from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langgraph.graph import END
from typing import Literal

from components.model import State, AgentConfig

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

        # Set my wallet address
        self.address = self.tools[3].invoke({"address": "0x00"})

    @staticmethod
    def route(state: State) -> Literal["putToken", "reporting"]:
        """
        Route the state to the appropriate agent based on the status.
        """
        if len(state.tokens) > 0:
            return "putToken"
        else:
            return "reporting"
    
    def init_prompt(self, state: State):
        """
        Initialize the prompt with agent state.
        """
        token_list = "\n".join(
            f"- トークンID: {token.token_id}, トークン名: {token.token_name}, 転送元アドレス: {token.from_address}, 転送先アドレス: {token.to_address}"
            for token in state.tokens
        ) if state.tokens else "発行されたトークンはありません。"

        if state.status == "putToken":
            system_message = """
            # Smart contract agent
            You are a smart contract agent that must call the put_token function to mint an NFT.
            
            **IMPORTANT**: You MUST call the put_token tool with the following parameters:
            - to_address: The wallet address for the NFT. Select the issuing address from the list of currently issued NFTs.
            - token_name: The name of the NFT to mint. Select the NFT name to be issued based on user role.
            
            Do not just provide information - you must execute the put_token function.
            """
        elif state.status == "reporting":
            system_message = """
            # Smart contract agent
            You are a smart contract agent that must call the reporting function to generate a final report.
            
            **IMPORTANT**: You MUST call the reporting tool to generate the final report.
            """
        else:
            system_message = """
            # Smart contract agent
            You are calling smart contract functions to support users as a smart contract agent.
            """

        # Define the prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ('system', system_message),
            (
                "system",
                """
                # List of currently issued tokens
                {token_list}
                """
            ),
            (
                "user",
                """
                # My information
                - Name: {name}
                - Role: {role}
                - Wallet address: {address}
                """
            )
        ])
        prompt = prompt_template.format_messages(
            token_list=token_list,
            name=self.name,
            role=self.roll,
            address=self.address
        )
        return prompt
    
    def execute(self, prompt):
        """
        Execute the agent with the given prompt and tools.
        """
        # Set  model with tools
        model_with_tool = self.model.bind_tools(self.tools)

        # Invoke the model with the prompt
        if self.config["callbacks"][0] == None:
            output = model_with_tool.invoke(prompt)
        else:
            output = model_with_tool.invoke(prompt, config=self.config)
        return output

    def get_agent(self, state: State) -> State:
        """
        Decide the next action based on the current state.
        """
        new_message = ""
        new_tokens = state.tokens
        new_address = state.address
        new_token_name = state.token_name
        new_status = state.status
        prompt = self.init_prompt(state)

        if(state.status == "fetchTokens"):
            new_tokens = self.tools[1].invoke("0x00")
            new_message = f"取引履歴が取得されました。トークンの数: {len(new_tokens)}"
            if len(new_tokens) > 0:
                new_status = "putToken"
            else:   
                new_status = "reporting"
        elif(state.status == "putToken"):
            output = self.execute(prompt)
            for tool_call in output.tool_calls:
                token_id = self.tools[0].invoke(tool_call["args"])
                new_message = f"NFTが発行されました。\n- トークンID: {token_id}\n- トークン名: {state.token_name}\n- 送信先アドレス: {state.address}"
                new_address = tool_call["args"]["to_address"]
                new_token_name = tool_call["args"]["token_name"]
            new_status = "reporting"
        elif(state.status == "reporting"):
            output = self.execute(prompt)
            for tool_call in output.tool_calls:
                new_message = self.tools[2].invoke(tool_call["args"])
            new_status = END

        # Return the state with updated messages and status
        return State(
            messages=[HumanMessage(content=new_message)],
            tokens=new_tokens,
            address=new_address,
            token_name=new_token_name,
            status=new_status,
        )
