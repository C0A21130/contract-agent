from langchain_core.tools import tool
from tools.contract import Contract

def get_tools(rpc_url: str, contract_address: str, private_key: str):
    
    # Set Smart Contract Instance
    contract = Contract(
        rpc_url=rpc_url,
        contract_address=contract_address,
        private_key=private_key,
    )

    # @tool
    # def add(x: int, y: int) -> int:
    #     """Add two numbers together."""
    #     return x + y

    # @tool
    # def sub(x: int, y: int) -> int:
    #     """Substract two numbers together."""
    #     return x - y
    
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

    return [set_name, get_name]
