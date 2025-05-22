from typing import List
from pydantic import BaseModel
from web3 import Web3
from tools.account import set_account
from tools.ssdlab_token_abi import abi

class Token(BaseModel):
    # This class is used to represent a token.
    from_address: str
    to_address: str
    token_id: int
    token_name: str

# This class is used to interact with a smart contract on the Ethereum blockchain.
class Contract:

    # This function initializes the Contract class with the given RPC URL, contract address, and private key.
    def __init__(self, rpc_url: str, contract_address: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract = None
        self.account = set_account(private_key=private_key)
        self.private_key = private_key
        
        # Connect to the Ethereum network
        if not self.w3.is_connected():
            raise Exception("Failed to connect to the Ethereum network")
        else:
            # create contract instance
            self.contract = self.w3.eth.contract(address=contract_address, abi=abi)
    
    # This function returns the address of the account.
    def get_address(self) -> str:
        # This function returns the address of the account.
        return self.account.address

    # This function sets the name in the smart contract.
    def set_name(self, name: str):
        # Call the setName function for smart contract
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx = self.contract.functions.setName(name).build_transaction({
            'chainId': 31337,
            'gas': 70000,
            "maxFeePerGas": self.w3.to_wei(2, 'gwei'),
            "maxPriorityFeePerGas": self.w3.to_wei(2, 'gwei'),
            'nonce': nonce,
        })

        # Sign and send the transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)

        # Send the transaction
        self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    # This function gets the name from the smart contract.
    def get_name(self) -> str:        
        # Call the getName function for smart contract
        return self.contract.functions.getName().call()

    # This function mints a NFT to the specified address.
    def mint(self, to_address: str, token_name: str) -> int:
        # Call the mint function for smart contract
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx = self.contract.functions.safeMint(to_address, token_name).build_transaction({
            'chainId': 31337,
            'gas': 200000,
            "maxFeePerGas": self.w3.to_wei(2, 'gwei'),
            "maxPriorityFeePerGas": self.w3.to_wei(2, 'gwei'),
            'nonce': nonce,
        })
        
        try:
            # Sign and send the transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for the transaction to be mined and get the transaction receipt to extract the token ID
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            token_id = tx_receipt.logs[0].topics[3].hex()

            return int(token_id, 16)
        except Exception as e:
            print(f"Error minting token: {e}")
            return -1

    # This function transfers a NFT from one address to another.    
    def transfer(self, from_address: str, to_address: str, token_id: str) -> None:
        # check if the from_address is the owner of the token
        if self.contract.functions.ownerOf(token_id).call() != from_address:
            raise Exception("You are not the owner of this token")

        # Call the transfer function for smart contract
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx = self.contract.functions.safeTransferFrom(from_address, to_address, token_id).build_transaction({
            'chainId': 31337,
            'gas': 200000,
            "maxFeePerGas": self.w3.to_wei(2, 'gwei'),
            "maxPriorityFeePerGas": self.w3.to_wei(2, 'gwei'),
            'nonce': nonce,
        })

        # Sign and send the transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for the transaction to be mined and get the transaction receipt to extract the token ID
        self.w3.eth.wait_for_transaction_receipt(tx_hash)

    # This function fetches all the tokens from the smart contract.
    def fetch_tokens(self) -> List[Token]:
        tokens: List[Token] = []
        logs = self.contract.events.Transfer().get_logs(from_block=0)
        for log in logs:
            # check if the log is mint the NFT
            if log["args"]["from"] == "0x0000000000000000000000000000000000000000":
                continue
            token = Token(
                from_address=log["args"]["from"],
                to_address=log["args"]["to"],
                token_id=log["args"]["tokenId"],
                token_name=self.contract.functions.getTokenName(log["args"]["tokenId"]).call()
            )
            tokens.append(token)

        return tokens
