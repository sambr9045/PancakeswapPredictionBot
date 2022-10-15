from datetime import datetime, timezone
from web3 import Web3
import json

class Base:
    def __init__(self,account_address,wallet_pk ,abi_path):
        self.wallet_pk = wallet_pk
        self.account_address = account_address
        self.RPC = "https://bsc-dataseed1.binance.org:443"
        self.WEB3 = Web3(Web3.HTTPProvider(self.RPC))
        self.abi_path = abi_path
        self.contract_address = "0x18B2A687610328590Bc8F2e5fEdDe3b582A49cdA"
        self.current_epoch = self.currentepock()
        self.chain_id = 56
        self.gas = 300000
        self.gas_price = Web3.toWei("5.5", "gwei")

    def nonce(self):
        nonce = self.WEB3.eth.getTransactionCount(self.account_address)
        return nonce

    def contract(self):
        # get abi
        with open(self.abi_path, "r") as abiFile:
            data = abiFile.read()
        abi = json.loads(data)
        contract = self.WEB3.eth.contract(address=self.contract_address, abi=abi)
        return contract

    def currentepock(self):
        return self.contract().functions.currentEpoch().call()

    def look_for_trade(self):
        # get current information
        current_rounds_list = self.contract().functions.rounds(self.current_epoch).call()
        lock_timestamp = current_rounds_list[2]
        total_amount = current_rounds_list[8]
        bull_amount = current_rounds_list[9]
        bear_amount = current_rounds_list[10]
        # Get current timestamp
        dt = int(datetime.now(timezone.utc).timestamp())
        time_remaining = lock_timestamp - dt
        # Calculate Ratio
        total_amount_normal = round(float(Web3.fromWei(total_amount, "ether")), 5)
        bull_amount_normal = round(float(Web3.fromWei(bull_amount, "ether")), 5)
        bear_amount_normal = round(float(Web3.fromWei(bear_amount, "ether")), 5)

        # Ratios
        if bull_amount_normal != 0 and bear_amount_normal != 0:
            bull_ratio = round(bull_amount_normal / bear_amount_normal, 2) + 1
            bear_ratio = round(bear_amount_normal / bull_amount_normal, 2) + 1
            # Ratios
        else:
            bull_ratio = 0
            bear_ratio = 0
        return [time_remaining, bull_ratio, bear_ratio]

    # send transaction
    def send_transaction(self, amount_in_bnb, bull_or_bear):
        amount = Web3.toWei(amount_in_bnb, "ether")
        tx_build = None
        if bull_or_bear == "bull":
            tx_build = self.contract().functions.betBull(self.current_epoch).buildTransaction({
                "chainId": self.chain_id,
                "value": amount,
                "gas": self.gas,
                "gasPrice": self.gas_price,
                "nonce": self.nonce()
            })
        if bull_or_bear == "bear":
            tx_build = self.contract().functions.betBear(self.current_epoch).buildTransaction({
                "chainId": self.chain_id,
                "value": amount,
                "gas": self.gas,
                "gasPrice": self.gas_price,
                "nonce": self.nonce()
            })

        self.send_raw_transaction(tx_build, self.wallet_pk)

    def claim_wining(self, epoch):
        # claim Winnings
        tx_build = self.contract().functions.claim([self.current_epoch]).buildTransaction({
            "chainId": self.chain_id,
            "gas": self.gas,
            "gasPrice": self.gas_price,
            "nonce": self.nonce()
        })
        self.send_raw_transaction(tx_build, self.wallet_pk)

    # check for winning
    def claimable(self, epock, address):
        claim = self.contract().functions.claimable(epock, address).call()
        return claim
        # check if found is claimable

    def send_raw_transaction(self, tx_build, wallet_pk):
        try:
            tx_signed = self.WEB3.eth.account.signTransaction(tx_build, wallet_pk)
            # sent_tx = self.WEB3.eth.sendRawTransaction(tx_signed.rawTransaction)
            sent_tx = self.WEB3.eth.send_raw_transaction(tx_signed.rawTransaction)
            return sent_tx
        except Exception as e:
            with open("logs.txt", 'a') as error:
                error.write(f":{e} \n")
            return "Failed to execute transaction"

    def wallet_balance(self):
        print(self.account_address)
        balance = self.WEB3.eth.get_balance(self.account_address)
        return self.WEB3.fromWei(int(balance), "ether")

    def send(self, amount, to):
        tx_build = {
            "chainId": self.chain_id,
            "value": self.WEB3.toWei(amount, "ether"),
            "gas": self.gas,
            "gasPrice": self.gas_price,
            "nonce": self.nonce(),
            "to":to
        }
        result = self.send_transaction(tx_build, self.wallet_pk)
        return result








