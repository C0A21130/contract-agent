from typing import Annotated, List
from langchain_core.tools import tool
from tools.contract import Contract, Token

def get_tools(rpc_url: str, contract_address: str, private_key: str):
    
    # Set Smart Contract Instance
    contract = Contract(
        rpc_url=rpc_url,
        contract_address=contract_address,
        private_key=private_key,
    )

    @tool
    def add(x: int, y: int) -> int:
        """Add two numbers together."""
        return x + y

    @tool
    def sub(x: int, y: int) -> int:
        """Substract two numbers together."""
        return x - y
    
    @tool
    def set_name(name: str) -> str:
        """
        This tool is called smart contract.
        Set name in smart contract.
        Args:
            name (str): User's name.
        Returns:
            str: Confirmation message.
        """
        contract.set_name(name)
        return f"Name set to {name} in smart contract."

    @tool
    def get_name() -> str:
        """
        This tool is called smart contract.
        Get User name from smart contract.
        Returns:
            str: User's name.
        """
        name = contract.get_name()
        return name

    @tool
    def put_token(
        to_address: Annotated[str, "The address to mint the token to"],
        token_name: Annotated[str, "The name of the token to mint"],
    ) -> int:
        """
        This tool is called smart contract.
        Mint a token to the specified address.
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
    def fetch_token(
        address: Annotated[str, "The address to fetch tokens from"],
    ) -> List[Token]:
        """
        This tool is called smart contract.
        Fetch all NFT(Non Fungible Token) for the address.
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

    return [add, sub, put_token, fetch_token]
