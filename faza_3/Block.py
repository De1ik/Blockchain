from Transaction import Transaction
import hashlib
from RSA import RSAHelper

class Block:
    COINBASE = 3.125

    def __init__(self, prev_hash, address):
        self.prev_block_hash = prev_hash
        self.coinbase = Transaction(coin=Block.COINBASE, address=address)
        self.txs = []
        self.hash = None

    def get_coinbase(self):
        return self.coinbase

    def get_hash(self):
        return self.hash

    def get_prev_block_hash(self):
        return self.prev_block_hash

    def get_transactions(self):
        return self.txs

    def get_transaction(self, index):
        return self.txs[index]

    def transaction_add(self, tx):
        self.txs.append(tx)

    def get_block(self):
        raw_block = bytearray()
        if self.prev_block_hash:
            raw_block.extend(self.prev_block_hash)
        for tx in self.txs:
            raw_block.extend(tx.get_tx())

        raw_block.extend(self.coinbase.get_tx())
        return bytes(raw_block)

    def finalize(self):
        self.hash = hashlib.sha256(self.get_block()).digest()