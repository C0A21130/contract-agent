import os
from dotenv import load_dotenv
from tools.tools import get_tools
from tools.contract import Token

# Load environment variables, but don't fail if .env doesn't exist
try:
    load_dotenv(verbose=True)
except:
    pass

# Get configuration with fallback to defaults
RPC_URL = os.environ["RPC_URL"]
CONTRACT_ADDRESS = os.environ["CONTRACT_ADDRESS"]
PRIVATE_KEY = os.environ["PRIVATE_KEY"]

def test_set_name():
    tools = get_tools(rpc_url=RPC_URL, contract_address=CONTRACT_ADDRESS, private_key=PRIVATE_KEY)
    set_name_tool = tools[0]
    get_name_tool = tools[1]
    set_name_tool.invoke("test")
    assert get_name_tool.invoke("call") == "test"

def test_put_token():
    tools = get_tools(rpc_url=RPC_URL, contract_address=CONTRACT_ADDRESS, private_key=PRIVATE_KEY)
    put_token_tool = tools[0]
    to_address = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    token_name = "Test Token"
    token_id = put_token_tool.invoke({"to_address": to_address, "token_name": token_name})
    assert token_id is not None
    assert token_id != -1
    
def test_fetch_token():
    tools = get_tools(rpc_url=RPC_URL, contract_address=CONTRACT_ADDRESS, private_key=PRIVATE_KEY)
    fetch_token_tool = tools[1]
    tokens = fetch_token_tool.invoke({"address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"})
    print(tokens)
    assert type(tokens) == list
    assert len(tokens) > 0
    for token in tokens:
        assert type(token) == Token
