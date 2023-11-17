from web3 import Web3
import os

class BlockchainHandler:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER')))
        self.contract = self.w3.eth.contract(
            address=os.getenv('CONTRACT_ADDRESS'),
            abi=os.getenv('CONTRACT_ABI')
        )

    def create_order_detail(self, order_detail_id, order_data):
        tx_hash = self.contract.functions.createOrderDetail(
            order_detail_id,
            order_data['product_id'],
            order_data['quantity'],
            order_data['price_each']
        ).transact({'from': self.w3.eth.accounts[0]})
        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        return receipt

# Example usage in app.py
# from blockchain import BlockchainHandler
# blockchain_handler = BlockchainHandler()
# receipt = blockchain_handler.create_order_detail(order_detail_id, order_data)
