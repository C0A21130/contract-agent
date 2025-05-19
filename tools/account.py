from eth_account import Account
from eth_account.signers.local import LocalAccount

def set_account(private_key: str) -> LocalAccount:
    # check account
    if private_key is None:
        raise Exception("Account is None")
    else:
        account = Account.from_key(private_key)
        return account
