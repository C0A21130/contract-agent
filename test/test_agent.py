import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
import pytest
from tools.tools import get_tools
from components.contract_agent import ContractAgent
from components.trust_agent import TrustAgent
from components.state import State, Token

load_dotenv(verbose=True)

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
    response = contract_agent.get_agent(state=state)

    print("messages: ", response["messages"])

    assert type(response["messages"]) == str
    assert response["tokens"] is not None
    assert response["status"] == "completed"

def test_fetch_token_agent():
    contract_agent = ContractAgent(model=model, tools=tools)
    state = State(
        messages=["test_message"],
        tokens=[],
        address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
        token_name="TEST TOKEN",
        status="fetch",
    )
    response = contract_agent.get_agent(state=state)

    print("message: ", response["messages"])
    print("status: ", response["status"])
    for token in response["tokens"]:
        print("---------------------")
        print("Token from address: ", token.from_address)
        print("Token to address: ", token.to_address)
        print("Token ID: ", token.token_id)
        print("Token name: ", token.token_name)

    assert type(response["messages"]) == str
    assert response["status"] == "trust"
    assert response["tokens"] is not None
    for token in response["tokens"]:
        assert type(token.from_address) == str
        assert type(token.to_address) == str
        assert type(token.token_id) == int
        assert type(token.token_name) == str

@pytest.mark.parametrize(
    [
        "state"
    ],
    [
        pytest.param(
            State(
                messages=["test_message"],
                tokens=[
                    Token(
                        from_address="0xdD2FD4581271e230360230F9337D5c0430Bf44C0",
                        to_address="0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199",
                        token_id=1,
                        token_name="Test Token 1"
                    )
                ],
                address="",
                token_name="",
                status="trust",
            ),
            id="trust_with_tokens",
        ),
        pytest.param(
            State(
                messages=["test_message"],
                tokens=[],
                address="",
                token_name="",
                status="trust",
            ),
            id="trust_without_tokens",
        ),
    ],
)
def test_trust_agent(state):
    trust_agent = TrustAgent(model=model)
    response = trust_agent.get_agent(
        state=state
    )

    print("messages: ", response["messages"])
    print("address: ", response["address"])
    print("token_name: ", response["token_name"])
    print("status: ", response["status"])

    assert type(response["messages"]) == str
    assert type(response["address"]) == str
    assert type(response["token_name"]) == str
    assert response["status"] == "put" or response["status"] == "fetch"
