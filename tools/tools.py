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
        This tool is called smart contract for minting the NFT.
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

    @tool
    def reporting(
        token_list: Annotated[str, "The document for list of currently NFTs"],
        token: Annotated[str, "The document for information of the token to be issued"],
        reason: Annotated[str, "The document for reason why the token is to be issued"],
        owner: Annotated[str, "The document for information of the owner"],
    ) -> str:
        """
        Report the current state of the agent.
        The report will be written in Japanese.
        """
        report = ""
        report += f"トークン一覧:\n {token_list}\n"
        report += f"発行するトークン:\n {token}\n"
        report += f"トークンを発行する理由:\n {reason}\n"
        report += f"送信先アドレス:\n {owner}\n"
        return report

    @tool
    def get_address() -> str:
        """
        Get my wallet address.
        """
        return contract.get_address()

    return [put_token, fetch_tokens, reporting, get_address]
