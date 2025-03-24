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


    def block_create(self, my_address):
        parent = self.blockchain.get_block_at_max_height().block
        parent_hash = parent.get_hash()
        new_block = Block(parent_hash, my_address)
        new_block.finalize()
        return new_block if self.blockchain.block_add(new_block) else None


    def tx_process(self, tx):
        self.blockchain.transaction_add(tx)
