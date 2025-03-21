import copy
from HandleTxs import HandleTxs
from UTXOPool import UTXOPool
from TransactionPool import TransactionPool
from UTXO import UTXO


# Meno študenta:
# Blockchain by mal na naplnenie funkcií udržiavať iba obmedzené množstvo uzlov
# Nemali by ste mať všetky bloky pridané do blockchainu v pamäti
# pretože by to mohlo spôsobiť pretečenie pamäte.
class Blockchain:
    CUT_OFF_AGE = 12

    class BlockNode:
        def __init__(self, block, parent, utxo_pool):
            self.block = block
            self.parent = parent
            self.children = []
            # utxo pool na vytvorenie nového bloku na vrchu tohto bloku
            self.utxo_pool = copy.deepcopy(utxo_pool)
            self.height = 1 if parent is None else parent.height + 1
            if parent:
                parent.children.append(self)

        def get_utxo_pool_copy(self):
            new_pool = UTXOPool()
            for utxo in self.utxo_pool.get_all_utxo():
                tx_output = self.utxo_pool.get_tx_output(utxo)
                new_pool.add_utxo(utxo, tx_output)
            return new_pool

    """    /**
     * vytvor prázdny blockchain iba s prvým (Genesis) blokom. Predpokladajme, že
     * {@code genesisBlock} je platný blok
     */"""
    def __init__(self, genesis_block):
        # Implementation required
        self.blockchain_dict = {}
        self.oldest_block_node = None
        self.newest_block_node = None
        self.utxo_pool = UTXOPool()
        self.tx_pool_dict = TransactionPool()
        # forks
        self.head_blocks = {}

        self.genesis_block_add(genesis_block)


    """/** Získaj najvyšší (maximum height) blok */"""
    def get_block_at_max_height(self):
        # Implementation required
        return self.newest_block_node

    """    /**
     * Získaj UTXOPool na ťaženie nového bloku na vrchu najvyššieho (max height)
     * bloku
     */"""
    def get_utxo_pool_at_max_height(self):
        # Implementation required
        return self.utxo_pool

    """/** Získaj pool transakcií na vyťaženie nového bloku */"""
    def get_transaction_pool(self):
        # Implementation required
        return self.tx_pool_dict

    """**
     * Pridaj {@code block} do blockchainu, ak je platný. Kvôli platnosti by mali
     * byť všetky transakcie platné a blok by mal byť na
     * {@code height > (maxHeight - CUT_OFF_AGE)}.
     *
     * Môžete napríklad vyskúšať vytvoriť nový blok nad blokom Genesis (výška bloku
     * 2), ak height blockchainu je {@code <=
     * CUT_OFF_AGE + 1}. Len čo {@code height > CUT_OFF_AGE + 1}, nemôžete vytvoriť
     * nový blok vo výške 2.
     *
     * @return true, ak je blok úspešne pridaný
     *"""
    def block_add(self, block):
        if block.prev_block_hash is None:
            return False

        parent_hash = block.prev_block_hash

        # check if the hash of prev block is correct
        if parent_hash not in self.blockchain_dict:
            return False

        parent_node = self.blockchain_dict[parent_hash]
        blockNode = self.BlockNode(block, parent=parent_node, utxo_pool=None)

        # check for the CUT_OFF_AGE
        if blockNode.height <= self.newest_block_node.height - self.CUT_OFF_AGE:
            return False

        try:
            # get all txs of the block
            utxo_pool = parent_node.get_utxo_pool_copy()
            coinbase_tx = blockNode.block.get_coinbase()
            block_txs = self.tx_pool_dict.get_transactions()

            block.txs.extend(block_txs)
            # process all txs, if txs is invalid then it will raise the error
            txs_handler = HandleTxs(utxo_pool)
            res = txs_handler.handler([coinbase_tx])
            res2 = txs_handler.handler(block_txs)

            new_utxo_pool = txs_handler.UTXOPoolGet()
            blockNode.utxo_pool = new_utxo_pool

            # update blockchain anf head of branches
            self.blockchain_dict[block.get_hash()] = blockNode
            self.head_blocks[block.get_hash()] = blockNode

            # del the prev block from the head of the branches
            if parent_hash in self.head_blocks:
                del self.head_blocks[parent_hash]

            # update the highest block
            if blockNode.height > self.newest_block_node.height:
                self.newest_block_node = blockNode
                self.utxo_pool = blockNode.get_utxo_pool_copy()

            self.remove_confirmed_transactions(block_txs)

        except Exception as e:
            print(e)
            return False

        return True

    def genesis_block_add(self, genesis_block):
        blockNode = self.BlockNode(genesis_block, parent=None, utxo_pool=None)

        # get all txs of the block
        utxo_pool = self.utxo_pool
        coinbase_tx = blockNode.block.get_coinbase()
        block_txs = blockNode.block.get_transactions()


        # process all txs, if txs is invalid then it will raise the error
        txs_handler = HandleTxs(utxo_pool)
        txs_handler.handler([coinbase_tx])
        txs_handler.handler(block_txs)

        new_utxo_pool = txs_handler.UTXOPoolGet()
        blockNode.utxo_pool = new_utxo_pool

        # update blockchain anf head of branches
        self.blockchain_dict[genesis_block.get_hash()] = blockNode
        self.head_blocks[genesis_block.get_hash()] = blockNode

        self.newest_block_node = blockNode
        # self.utxo_pool = blockNode.get_utxo_pool_copy()
        self.utxo_pool = blockNode.utxo_pool

        self.remove_confirmed_transactions(block_txs)

    """/** Pridaj transakciu do transakčného poolu */"""
    def transaction_add(self, tx):
        # Implementation required
        if tx in self.tx_pool_dict.get_transactions():
            return False

        if not HandleTxs.txIsValid(tx, self.utxo_pool):
            print('NOT VALID')
            raise Exception
            return False


        self.tx_pool_dict.add_transaction(tx)
        return True


    def remove_confirmed_transactions(self, block_txs):
        for tx in block_txs:
            self.tx_pool_dict.remove_transaction(tx.get_hash())
