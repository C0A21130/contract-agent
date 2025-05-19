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

RPC_URL = "http://10.203.92.71:8545"
CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

tools = get_tools(
    rpc_url=RPC_URL,
    contract_address=CONTRACT_ADDRESS,
    private_key=os.environ["PRIVATE_KEY"],
)

# def test_write_agent():
#     contract_agent = ContractAgent(model=model, tools=tools)
#     state = State(
#         message=["test_message"],
#         name="test_name",
#         status="trust",
#     )
#     response = contract_agent.put_name_agent(state=state)

#     for res in response["messages"]:
#         print(res)
#         print("-------------")
#     print(response["status"])

#     assert response["status"] == "completed"
#     assert response["messages"] is not None

def test_read_agent():
    contract_agent = ContractAgent(model=model, tools=tools)
    response = contract_agent.get_name_agent(state=None)
    for res in response["message"]:
        print(res)
        print("-------------")

    print(response["status"])

    assert response["status"] == "completed" or response["status"] == "trust"
    assert response["message"] is not None

def test_trust_agent():
    trust_agent = TrustAgent(model=model)
    response = trust_agent.eval_trust(state=None)

    for res in response["message"]:
        print(res)
        print("-------------")
    print(response["status"])
    print(response["name"])

    assert response["status"] == "put" or response["status"] == "fetch"
    assert response["message"] is not None
    assert response["name"] is not None
