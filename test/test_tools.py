import os
from dotenv import load_dotenv
from tools.tools import get_tools

load_dotenv(verbose=True)

RPC_URL = "http://localhost:8545"
CONTRACT_ADDRESS = '0x5FbDB2315678afecb367f032d93F642f64180aa3'
PRIVATE_KEY = os.environ["PRIVATE_KEY"]

def test_set_name():
    tools = get_tools(rpc_url=RPC_URL, contract_address=CONTRACT_ADDRESS, private_key=PRIVATE_KEY)
    set_name_tool = tools[0]
    get_name_tool = tools[1]
    set_name_tool.invoke("test")
    assert get_name_tool.invoke("call") == "test"
