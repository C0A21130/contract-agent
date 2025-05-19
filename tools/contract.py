from web3 import Web3
from tools.account import set_account
from tools.name_abi import abi

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
