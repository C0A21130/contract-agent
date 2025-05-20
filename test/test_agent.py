import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from tools.tools import get_tools
from components.contract_agent import ContractAgent
from components.trust_agent import TrustAgent
from components.state import State

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

def test_write_agent():
    contract_agent = ContractAgent(model=model, tools=tools)
    state = State(
        message=["test_message"],
        name="test_name",
        status="trust",
    )
    response = contract_agent.put_name_agent(state=state)

    print("message: ", response["message"])
    print("status: ", response["status"])

    assert type(response["message"]) == str
    assert response["status"] == "completed"

def test_read_agent():
    state = State(
        messages=["test_message"],
        name="test_name",
        status="trust",
    )
    contract_agent = ContractAgent(model=model, tools=tools)
    response = contract_agent.get_name_agent(state=state)
    print("message: ", response["messages"])
    print("status: ", response["status"])
    print("name: ", response["name"])

    assert response["messages"] is not None
    assert response["status"] == "completed" or response["status"] == "trust"
    assert response["name"] is not None

def test_trust_agent():
    trust_agent = TrustAgent(model=model)
    response = trust_agent.eval_trust_agent(state=None)

    print("messages: ", response["messages"])
    print("status: ", response["status"])

    assert response["status"] == "put" or response["status"] == "fetch"
    assert response["messages"] is not None
    assert response["name"] is not None
