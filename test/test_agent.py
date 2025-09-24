import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from tools.tools import get_tools
from components.contract_agent import ContractAgent
from components.model import State, AgentConfig

try:
    load_dotenv(verbose=True)
except:
    pass

# set model
model = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

RPC_URL = os.environ["RPC_URL"]
CONTRACT_ADDRESS = os.environ["CONTRACT_ADDRESS"]

tools = get_tools(
    rpc_url=RPC_URL,
    contract_address=CONTRACT_ADDRESS,
    private_key=os.environ["PRIVATE_KEY"],
)

def test_put_token_agent():
    contract_agent = ContractAgent(model=model, tools=tools)
    state = State(
        messages=["test_message"],
        tokens=[],
        address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
        token_name="TEST TOKEN",
        status="put",
    )
    response = contract_agent.get_bind_tool_agent(state=state)

    print("messages: ", response["messages"])

    assert type(response["messages"]) == str
    assert response["tokens"] is not None
    assert response["status"] == "completed"

def test_fetch_token_agent():
    contract_agent = ContractAgent(
        model=model,
        config=AgentConfig( 
            tools=tools,
            name="contract_agent",
            roll="This agent interacts with a smart contract to mint and transfer NFTs.",
        ),
    )
    state = State(
        messages=[],
        tokens=[],
        address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
        token_name="TEST TOKEN",
        status="fetch",
    )
    response = contract_agent.get_bind_tool_agent(state=state)
    print("response: ", response)

    print("message: ", response["messages"])
    print("status: ", response["status"])
    for token in response["tokens"]:
        print("---------------------")
        print("Token from address: ", token.from_address)
        print("Token to address: ", token.to_address)
        print("Token ID: ", token.token_id)
        print("Token name: ", token.token_name)

    assert response["tokens"] is not None
    for token in response["tokens"]:
        assert type(token.from_address) == str
        assert type(token.to_address) == str
        assert type(token.token_id) == int
        assert type(token.token_name) == str
