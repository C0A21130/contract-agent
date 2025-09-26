import os
from dotenv import load_dotenv
from tools.tools import get_tools
from tools.contract import Token
import pytest

# Load environment variables, but don't fail if .env doesn't exist
try:
    load_dotenv(verbose=True)
except:
    pass

# Get configuration with fallback to defaults
RPC_URL = os.environ["RPC_URL"]
CONTRACT_ADDRESS = os.environ["CONTRACT_ADDRESS"]
PRIVATE_KEY = os.environ["PRIVATE_KEY"]

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

@pytest.mark.parametrize("token_list,token,reason,owner,expected_contains", [
    (
        "Token1, Token2, Token3",
        "New Gaming NFT",
        "Reward for completing quest",
        "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
        ["トークン一覧:\n Token1, Token2, Token3\n", "発行するトークン:\n New Gaming NFT\n", "トークンを発行する理由:\n Reward for completing quest\n", "送信先アドレス:\n 0x70997970C51812dc3A010C7d01b50e0d17dc79C8\n"]
    ),
    (
        "Digital Art Collection",
        "Masterpiece #001",
        "Artist collaboration event",
        "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        ["トークン一覧:\n Digital Art Collection\n", "発行するトークン:\n Masterpiece #001\n", "トークンを発行する理由:\n Artist collaboration event\n", "送信先アドレス:\n 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266\n"]
    ),
    (
        "",
        "First Token",
        "Initial mint",
        "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
        ["トークン一覧:\n \n", "発行するトークン:\n First Token\n", "トークンを発行する理由:\n Initial mint\n", "送信先アドレス:\n 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC\n"]
    )
])
def test_reporting(token_list, token, reason, owner, expected_contains):
    tools = get_tools(rpc_url=RPC_URL, contract_address=CONTRACT_ADDRESS, private_key=PRIVATE_KEY)
    reporting_tool = tools[2]
    try:
        report = reporting_tool.invoke({
            "token_list": token_list,
            "token": token,
            "reason": reason,
            "owner": owner
        })
        
        assert isinstance(report, str)
        for expected_text in expected_contains:
            assert expected_text in report
            
    except UnboundLocalError:
        # If the bug exists, we expect this error
        pytest.fail("reporting function has UnboundLocalError - report variable not initialized")
