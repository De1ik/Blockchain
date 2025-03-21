from Block import Block
from HandleTxs import HandleTxs

class HandleBlocks:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    """* pridaj {@code block} do blockchainu ak je platný.
     * 
     * @return true ak je blok platný a bol pridaný, inak false
     */"""
    def block_process(self, block):
        if block is None:
            return False
        return self.blockchain.block_add(block)

    # def block_create(self, my_address):
    #     parent = self.blockchain.get_block_at_max_height()
    #     parent_hash = parent.get_hash()
    #     current = Block(parent_hash, my_address)
    #     utxo_pool = self.blockchain.get_utxo_pool_at_max_height()
    #     tx_pool = self.blockchain.get_transaction_pool()
    #     handler = HandleTxs(utxo_pool)
    #     txs = tx_pool.get_transactions()
    #     r_txs = handler.handler(txs)
    #     for tx in r_txs:
    #         current.transaction_add(tx)
    #     current.finalize()
    #     return current if self.blockchain.block_add(current) else None

    def block_create(self, my_address):
        parent = self.blockchain.get_block_at_max_height()
        parent_hash = parent.get_hash()
        current = Block(parent_hash, my_address)
        utxo_pool = self.blockchain.get_utxo_pool_at_max_height()
        tx_pool = self.blockchain.get_transaction_pool()
        handler = HandleTxs(utxo_pool)
        txs = tx_pool.get_transactions()
        r_txs = handler.handler(txs)
        for tx in r_txs:
            current.transaction_add(tx)
        current.finalize()
        return current if self.blockchain.block_add(current) else None

    def tx_process(self, tx):
        self.blockchain.transaction_add(tx)
