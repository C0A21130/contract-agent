import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from tools.tools import get_tools
from tools.contract import Token
from components.contract_agent import ContractAgent
from components.model import State, AgentConfig
import pytest

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
tools = get_tools(
    rpc_url=os.environ["RPC_URL"],
    contract_address=os.environ["CONTRACT_ADDRESS"],
    private_key=os.environ["PRIVATE_KEY"],
)

@pytest.mark.parametrize("state,expected_response", [
    (
        State(
            messages=[],
            tokens=[
                Token(
                    from_address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
                    to_address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
                    token_id=1,
                    token_name="TEST TOKEN",
                )
            ],
            address="",
            token_name="" ,
            status="putToken",
        ),
        {
            "status": "reporting",
            "message_type": str,
            "tokens_not_none": True,
            "expected_content": ["NFTが発行されました"]
        }
    ),
    (
        State(
            messages=[],
            tokens=[
                Token(
                    from_address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
                    to_address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
                    token_id=1,
                    token_name="TEST TOKEN",
                ),
                Token(
                    from_address="0xbDA5747bFD65F08deb54cb465eB87D40e51B197E",
                    to_address="0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199",
                    token_id=2,
                    token_name="TEST TOKEN 2",
                )
            ],
            address="",
            token_name="" ,
            status="putToken",
        ),
        {
            "status": "reporting",
            "message_type": str,
            "tokens_not_none": True,
            "expected_content": ["NFTが発行されました"]
        }
    ),
])
def test_agent_for_put_token(state, expected_response):
    contract_agent = ContractAgent(
        model=model,
        config=AgentConfig( 
            tools=tools,
            name="contract_agent",
            roll="This agent interacts with a smart contract to mint and transfer NFTs.",
        ),
    )
    response = contract_agent.get_agent(state=state)

    print("messages: ", response.messages)

    # expected_responseを使用した検証
    assert isinstance(response.messages[0].content, expected_response["message_type"])
    assert (response.tokens is not None) == expected_response["tokens_not_none"]
    assert response.status == expected_response["status"]
    
    # 期待されるコンテンツが含まれているかチェック
    message_content = response.messages[0].content
    for expected_text in expected_response["expected_content"]:
        assert expected_text in message_content

@pytest.mark.parametrize("state,expected_response", [
    (
        State(
            messages=[],
            tokens=[],
            address="",
            token_name="",
            status="fetchTokens",
        ),
        {
            "tokens_not_none": True,
            "token_attributes": ["from_address", "to_address", "token_id", "token_name"],
            "token_types": [str, str, int, str],
            "status_options": ["putToken", "reporting"]  # どちらかになる可能性
        }
    ),
])
def test_agent_for_fetch_tokens(state, expected_response):
    contract_agent = ContractAgent(
        model=model,
        config=AgentConfig( 
            tools=tools,
            name="contract_agent",
            roll="This agent interacts with a smart contract to mint and transfer NFTs.",
        ),
    )
    response = contract_agent.get_agent(state=state)
    print("response: ", response)

    print("message: ", response.messages)
    print("status: ", response.status)
    for token in response.tokens:
        print("---------------------")
        print("Token from address: ", token.from_address)
        print("Token to address: ", token.to_address)
        print("Token ID: ", token.token_id)
        print("Token name: ", token.token_name)

    # expected_responseを使用した検証
    assert (response.tokens is not None) == expected_response["tokens_not_none"]
    assert response.status in expected_response["status_options"]
    
    # トークンの型検証
    for token in response.tokens:
        for attr, expected_type in zip(expected_response["token_attributes"], expected_response["token_types"]):
            assert hasattr(token, attr)
            assert type(getattr(token, attr)) == expected_type

@pytest.mark.parametrize("state,expected_response", [
    # Case 1: NFTを発行していない場合のレポート
    (
        State(
            messages=[],
            tokens=[],
            address="",
            token_name="",
            status="reporting",
        ),
        {
            "status": "__end__",
            "messages_not_empty": True,
            "token_count": 0,
            "description": "NFTを発行していない場合のレポート"
        }
    ),
    # Case 2: 1つのNFTを発行している場合のレポート
    (
        State(
            messages=[],
            tokens=[
                Token(
                    from_address="0x0000000000000000000000000000000000000000",
                    to_address="0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
                    token_id=1,
                    token_name="Gaming Achievement NFT",
                )
            ],
            address="0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
            token_name="Gaming Achievement NFT",
            status="reporting",
        ),
        {
            "status": "__end__",
            "messages_not_empty": True,
            "token_count": 1,
            "description": "1つのNFTを発行している場合のレポート"
        }
    ),
    # Case 3: 複数のNFTを発行している場合のレポート
    (
        State(
            messages=[],
            tokens=[
                Token(
                    from_address="0x0000000000000000000000000000000000000000",
                    to_address="0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
                    token_id=1,
                    token_name="Gaming Achievement NFT",
                ),
                Token(
                    from_address="0x0000000000000000000000000000000000000000",
                    to_address="0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
                    token_id=2,
                    token_name="Art Collection NFT",
                ),
                Token(
                    from_address="0x0000000000000000000000000000000000000000",
                    to_address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
                    token_id=3,
                    token_name="Rare Digital Asset",
                )
            ],
            address="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
            token_name="New Token to Issue",
            status="reporting",
        ),
        {
            "status": "__end__",
            "messages_not_empty": True,
            "token_count": 3,
            "description": "複数のNFTを発行している場合のレポート"
        }
    ),
])
def test_agent_for_reporting(state, expected_response):
    contract_agent = ContractAgent(
        model=model,
        config=AgentConfig( 
            tools=tools,
            name="contract_agent",
            roll="This agent interacts with a smart contract to mint and transfer NFTs.",
        ),
    )
    response = contract_agent.get_agent(state=state)
    print(f"Testing: {expected_response['description']}")
    print("response: ", response)

    # expected_responseを使用した基本検証
    assert response.messages is not None
    assert (len(response.messages) > 0) == expected_response["messages_not_empty"]
    assert response.status == expected_response["status"]
    
    # トークン数の検証
    print(f"Expected token count: {expected_response['token_count']}, Actual: {len(state.tokens)}")
    assert len(state.tokens) == expected_response["token_count"]
    
    # トークン情報の出力（デバッグ用）
    if len(state.tokens) > 0:
        print(f"Number of tokens in state: {len(state.tokens)}")
        for i, token in enumerate(state.tokens):
            print(f"Token {i+1}: {token.token_name}")
    else:
        print("No tokens in state - testing empty token list scenario")
