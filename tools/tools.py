from typing import Annotated, List
from langchain_core.tools import tool
from tools.contract import Contract, Token

def get_tools(rpc_url: str, contract_address: str, private_key: str) -> List[tool]:
    
    # Set Smart Contract Instance
    contract = Contract(
        rpc_url=rpc_url,
        contract_address=contract_address,
        private_key=private_key,
    )

    @tool
    def put_token(
        to_address: Annotated[str, "The address to mint the token to"],
        token_name: Annotated[str, "The name of the token to mint"],
    ) -> int:
        """
        This tool is called smart contract.
        Mint a NFT to the specified address.
        Returns:
            int: The token ID of the minted NFT.
        """
        from_address = contract.get_address()
        token_id = contract.mint(from_address, token_name)
        if token_id == -1:
            return -1
        else:
            contract.transfer(from_address, to_address, token_id)
            return token_id

    @tool
    def fetch_tokens(
        address: Annotated[str | None, "The address to fetch tokens from"],
    ) -> List[Token]:
        """
        This tool is called smart contract.
        Fetch all NFTs transaction history for the address.
        Returns:
            List[Token]:
            Token: {
                "from_address": str,
                "to_address": str,
                "token_id": int,
                "token_name": str,
            }
        1. from_address: The address to which the token to transfer.
        2. to_address: The address where you received the NFT.
        3. token_id: The ID of the token.
        4. token_name: The name of the token.
        """
        tokens = contract.fetch_tokens()
        return tokens

    return [put_token, fetch_tokens]
