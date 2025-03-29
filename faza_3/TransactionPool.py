from ByteArrayWrapper import ByteArrayWrapper

class TransactionPool:
    def __init__(self, tx_pool=None):
        self.transactions = dict(tx_pool.transactions) if tx_pool else {}

    def add_transaction(self, tx):
        tx_hash = ByteArrayWrapper(tx.get_hash())  # Ensure tx.get_hash() is called correctly
        self.transactions[tx_hash] = tx

    def remove_transaction(self, tx_hash):
        tx_hash_wrapper = ByteArrayWrapper(tx_hash)
        self.transactions.pop(tx_hash_wrapper, None)  # Fix: Closing parenthesis added

    def get_transaction(self, tx_hash):
        tx_hash_wrapper = ByteArrayWrapper(tx_hash)
        return self.transactions.get(tx_hash_wrapper)

    def get_transactions(self):
        return list(self.transactions.values())
