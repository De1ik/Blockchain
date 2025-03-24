import unittest
from importlib import invalidate_caches

from RSA import RSAHelper
from Transaction import Transaction
from UTXO import UTXO
from UTXOPool import UTXOPool
from HandleTxs import HandleTxs

from Block import Block
from Blockchain import Blockchain
from HandleBlocks import HandleBlocks



class HandleTxsTest(unittest.TestCase):

    def test_process_block_without_transaction(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()

        result = handle_blocks.block_process(block1)

        self.assertTrue(result, "Block without transaction was processed successfully")
        self.assertEqual(blockchain.get_block_at_max_height().block, block1, "Block must be the head of the blockchain")

    def test_process_block_one_valid_transaction(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        tx0 = Transaction()

        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(1, address=alice.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx0.add_signature(signature, 0)
        tx0.finalize()

        blockchain.transaction_add(tx0)

        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()
        result = handle_blocks.block_process(block1)

        utxo_pool = blockchain.get_utxo_pool_at_max_height()
        spent_utxo = UTXO(genesis_block.coinbase.get_hash(), 0)
        new_utxo = UTXO(tx0.get_hash(), 0)

        self.assertTrue(result, "Block with one valid transaction was processed successfully")
        self.assertEqual(blockchain.get_block_at_max_height().block, block1, "Block must be the head of the blockchain")
        self.assertIn(tx0, block1.get_transactions(), "Transaction must be in new block")
        self.assertFalse(utxo_pool.contains(spent_utxo), "Used UTXO must be removed")
        self.assertTrue(utxo_pool.contains(new_utxo), "New UTXO must be in new group")

    def test_process_block_many_valid_transaction(self):
        bob = RSAHelper()
        alice = RSAHelper()
        mark = RSAHelper()
        dima = RSAHelper()
        masha = RSAHelper()
        artem = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)


        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(0.5, address=alice.public_key)
        tx0.add_output(0.5, address=mark.public_key)
        tx0.add_output(0.5, address=dima.public_key)
        tx0.add_output(0.5, address=masha.public_key)
        tx0.add_output(0.5, address=masha.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx0.add_signature(signature, 0)
        tx0.finalize()

        blockchain.transaction_add(tx0)

        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()
        result1 = handle_blocks.block_process(block1)


        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(0.5, address=artem.public_key)
        data_to_sign = tx1.get_data_to_sign(0)
        signature = alice.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()

        tx2 = Transaction()
        tx2.add_input(tx0.get_hash(), 1)
        tx2.add_output(0.5, address=artem.public_key)
        data_to_sign = tx2.get_data_to_sign(0)
        signature = mark.sign(data_to_sign)
        tx2.add_signature(signature, 0)
        tx2.finalize()

        tx3 = Transaction()
        tx3.add_input(tx0.get_hash(), 2)
        tx3.add_output(0.5, address=artem.public_key)
        data_to_sign = tx3.get_data_to_sign(0)
        signature = dima.sign(data_to_sign)
        tx3.add_signature(signature, 0)
        tx3.finalize()

        tx4 = Transaction()
        tx4.add_input(tx0.get_hash(), 3)
        tx4.add_input(tx0.get_hash(), 4)
        tx4.add_output(1.0, address=artem.public_key)
        data_to_sign = tx4.get_data_to_sign(0)
        signature = masha.sign(data_to_sign)
        tx4.add_signature(signature, 0)
        data_to_sign_1 = tx4.get_data_to_sign(1)
        signature_1 = masha.sign(data_to_sign_1)
        tx4.add_signature(signature_1, 1)
        tx4.finalize()


        blockchain.transaction_add(tx1)
        blockchain.transaction_add(tx2)
        blockchain.transaction_add(tx3)
        blockchain.transaction_add(tx4)

        block2 = Block(block1.get_hash(), alice.public_key)
        block2.finalize()
        result2 = handle_blocks.block_process(block2)

        # tx5 = Transaction()
        # tx5.add_input(tx1.get_hash(), 0) #0.5
        # tx5.add_input(tx2.get_hash(), 0) #0.5
        # tx5.add_input(tx3.get_hash(), 0) #0.5
        # tx5.add_input(tx4.get_hash(), 0) #1.0
        # tx5.add_output(2.5, address=alice.public_key)
        #
        # data_to_sign = tx5.get_data_to_sign(0)
        # signature = artem.sign(data_to_sign)
        # tx5.add_signature(signature, 0)
        #
        # data_to_sign = tx5.get_data_to_sign(1)
        # signature = artem.sign(data_to_sign)
        # tx5.add_signature(signature, 1)
        #
        # data_to_sign = tx5.get_data_to_sign(2)
        # signature = artem.sign(data_to_sign)
        # tx5.add_signature(signature, 2)
        #
        # data_to_sign = tx5.get_data_to_sign(3)
        # signature = artem.sign(data_to_sign)
        # tx5.add_signature(signature, 3)
        #
        # tx5.finalize()
        #
        # blockchain.transaction_add(tx5)
        #
        # block3 = Block(block2.get_hash(), alice.public_key)
        # block3.finalize()
        # result3 = handle_blocks.block_process(block3)


        self.assertTrue(result1, "Block1 with tx0 must be processed successfully")
        self.assertTrue(result2, "Block 2 with tx1-tx4 must be accepted")
        # self.assertTrue(result3, "Block 3 with tx1-tx4 must be accepted")
        self.assertEqual(blockchain.get_block_at_max_height().block, block2, "Block 2 should be the top of the chain")

        utxo_pool = blockchain.get_utxo_pool_at_max_height()
        spent_utxo = UTXO(genesis_block.get_coinbase().get_hash(), 0)

        self.assertFalse(utxo_pool.contains(spent_utxo), "UTXO from Genesis needs to be spent")
        self.assertFalse(utxo_pool.contains(UTXO(tx0.get_hash(), 2)), f"The output 1 of tx0 must be spent")

        for i in range(4):
            self.assertFalse(utxo_pool.contains(UTXO(tx0.get_hash(), i)), f"The output {i} of tx0 must be spent")

    def test_process_block_double_spend_transaction(self):
        bob = RSAHelper()
        alice = RSAHelper()


        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)


        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(3.0, address=alice.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx0.add_signature(signature, 0)
        tx0.finalize()

        # create invalid tx with the same UTXO
        tx1 = Transaction()
        tx1.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx1.add_output(3.0, address=alice.public_key)
        data_to_sign = tx1.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()

        is_added_tx0 = blockchain.transaction_add(tx0)
        is_added_tx1 = blockchain.transaction_add(tx1)

        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()
        is_block1_added = handle_blocks.block_process(block1)

        self.assertTrue(is_added_tx0, "Tx0 is valid and must be added to the pool of txs")
        self.assertFalse(is_added_tx1, "Tx1 is invalid (due to double spend) and can not be added to the pool of txs")
        self.assertTrue(is_block1_added, "Block1 with valid tx0 must be processed successfully")
        self.assertEqual(blockchain.get_block_at_max_height().block, block1, "Block 1 should be added to the chain and become the top of the leader")

        utxo_pool = blockchain.get_utxo_pool_at_max_height()
        basic_utxo = UTXO(genesis_block.get_coinbase().get_hash(), 0)

        self.assertFalse(utxo_pool.contains(basic_utxo), "UTXO from Genesis was spent by tx0")

        self.assertTrue(tx0 in blockchain.get_block_at_max_height().block.get_transactions(),  "TX0 must be in the list of valid transactions")
        self.assertFalse(tx1 in blockchain.get_block_at_max_height().block.get_transactions(),  "TX1 can not be in the list of valid transactions")

    def test_process_block_new_genesis(self):
        bob = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        new_genesis_block = Block(None, bob.public_key)
        new_genesis_block.finalize()

        result = handle_blocks.block_process(new_genesis_block)

        self.assertFalse(result, "New genesis blck can not be processed successfully")
        self.assertEqual(blockchain.get_block_at_max_height().block, genesis_block, "Genesis block must be the head of the blockchain")

    def test_process_block_invalid_prev_hash(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        invalid_prev_block_hash = bytearray(genesis_block.get_hash())
        invalid_prev_block_hash[-1] ^= 0x01
        invalid_prev_block_hash = bytes(invalid_prev_block_hash)

        block1 = Block(invalid_prev_block_hash, alice.public_key)
        block1.finalize()

        is_block1_added = handle_blocks.block_process(block1)

        self.assertFalse(is_block1_added, "Block1 with incorrect prev hash can not be processed successfully")
        self.assertEqual(blockchain.get_block_at_max_height().block, genesis_block, "Genesis block must remain the head of the blockchain")

    def test_process_block_different_invalid_transaction(self):
        bob = RSAHelper()
        alice = RSAHelper()


        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        # INVALID SIGNATURE: create invalid tx with incorrect signature
        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 1)
        tx0.add_output(1.0, address=alice.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        invalid_signature = bytearray(signature)
        invalid_signature[-1] ^= 0x01
        invalid_signature = bytes(invalid_signature)
        tx0.add_signature(invalid_signature, 0)
        tx0.finalize()

        # INVALID OUTPUT VALUE: the output value more than input value
        tx1 = Transaction()
        tx1.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx1.add_output(5.0, address=alice.public_key) #input 3.0 -> output 5.0
        data_to_sign = tx1.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()

        # INVALID UTXO: utxo is not exists
        tx2 = Transaction()
        tx2.add_input(tx0.get_hash(), 0)
        tx2.add_output(2.0, address=alice.public_key)
        data_to_sign = tx2.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx2.add_signature(signature, 0)
        tx2.finalize()

        # INVALID VERIFY DUE ADDRESS: try to sign with another key
        tx3 = Transaction()
        tx3.add_input(tx0.get_hash(), 0)
        tx3.add_output(2.0, address=alice.public_key)
        data_to_sign = tx3.get_data_to_sign(0)
        signature = alice.sign(data_to_sign)
        tx3.add_signature(signature, 0)
        tx3.finalize()

        # VALID tx
        tx_v = Transaction()
        tx_v.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx_v.add_output(3, address=alice.public_key)
        data_to_sign = tx_v.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx_v.add_signature(signature, 0)
        tx_v.finalize()


        # DOUBLE SPENDING: create invalid tx with the same UTXO
        tx4 = Transaction()
        tx4.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx4.add_output(1.0, address=alice.public_key)
        data_to_sign = tx4.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx4.add_signature(signature, 0)
        tx4.finalize()



        blockchain.transaction_add(tx0) # invalid signature
        blockchain.transaction_add(tx1) # invalid output
        blockchain.transaction_add(tx2) # invalid utxo
        blockchain.transaction_add(tx3) # invalid address to verify
        blockchain.transaction_add(tx_v) # valid tx
        blockchain.transaction_add(tx4) # invalid due double spend

        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()
        is_block1_added = handle_blocks.block_process(block1)


        self.assertTrue(is_block1_added, "Block1 with valid tx_v must be processed successfully")
        self.assertEqual(blockchain.get_block_at_max_height().block, block1, "Block 1 should be added to the chain nd become the leader")

        utxo_pool = blockchain.get_utxo_pool_at_max_height()
        basic_utxo = UTXO(genesis_block.get_coinbase().get_hash(), 0)

        self.assertFalse(utxo_pool.contains(basic_utxo), "UTXO from Genesis was spent")

        for tx in [tx0, tx1, tx2, tx3, tx4]:
            self.assertFalse(tx in blockchain.get_block_at_max_height().block.get_transactions(),  "tx can not be in the list of valid transactions")

    # 8
    def test_process_block_many_blocks_on_genesis(self):
        bob = RSAHelper()
        alice = RSAHelper()
        dima = RSAHelper()
        artem = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        block1 = Block(genesis_block.get_hash(), bob.public_key)
        block1.finalize()

        block2 = Block(genesis_block.get_hash(), alice.public_key)
        block2.finalize()

        block3 = Block(genesis_block.get_hash(), dima.public_key)
        block3.finalize()

        block4 = Block(genesis_block.get_hash(), artem.public_key)
        block4.finalize()

        is_block1_added = handle_blocks.block_process(block1)
        is_block2_added = handle_blocks.block_process(block2)
        is_block3_added = handle_blocks.block_process(block3)
        is_block4_added = handle_blocks.block_process(block4)

        self.assertTrue(is_block1_added, "Block1 without transaction was processed successfully on genesis")
        self.assertTrue(is_block2_added, "Block2 without transaction was processed successfully on genesis")
        self.assertTrue(is_block3_added, "Block3 without transaction was processed successfully on genesis")
        self.assertTrue(is_block4_added, "Block4 without transaction was processed successfully on genesis")

        # all blocks have the same height, but block 1 reached this height first
        self.assertEqual(blockchain.get_block_at_max_height().block, block1, "Block must be the head of the blockchain")

        self.assertTrue(block1.get_hash() in blockchain.get_head_blocks().keys(), "Block1 without transaction was processed successfully directly on genesis / height 1")
        self.assertTrue(block2.get_hash() in blockchain.get_head_blocks().keys(), "Block2 without transaction was processed successfully directly on genesis / height 1")
        self.assertTrue(block3.get_hash() in blockchain.get_head_blocks().keys(), "Block3 without transaction was processed successfully directly on genesis / height 1")
        self.assertTrue(block4.get_hash() in blockchain.get_head_blocks().keys(), "Block4 without transaction was processed successfully directly on genesis / height 1")

    # 9
    def test_process_block_utxo_from_parent_transaction(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(1, address=alice.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx0.add_signature(signature, 0)
        tx0.finalize()

        is_tx0_added = blockchain.transaction_add(tx0)
        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()
        is_block1_added = handle_blocks.block_process(block1)


        tx1 = Transaction()
        tx1.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx1.add_output(1, address=alice.public_key)
        data_to_sign = tx1.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()

        is_tx1_added = blockchain.transaction_add(tx1)
        block2 = Block(block1.get_hash(), alice.public_key)
        block2.finalize()
        is_block2_added = handle_blocks.block_process(block2)

        self.assertTrue(is_tx0_added, "Tx0 is valid and was processed successfully")
        self.assertFalse(is_tx1_added, "Tx1 is not valid and was not processed successfully")

        self.assertTrue(is_block1_added, "Block1 with one valid transaction was processed successfully")
        self.assertTrue(is_block2_added, "Block2 with no transaction was processed successfully")

        self.assertEqual(blockchain.get_block_at_max_height().block, block2, "Block2 must be the head of the blockchain")

        self.assertTrue(tx0.get_hash() == block1.get_transactions()[0].get_hash(), "TX0 must be in block1")
        self.assertTrue(0 == len(block2.get_transactions()), "Tx1 can not be in block2")

    # 10
    def test_process_block_utxo_from_another_branch(self):
        bob = RSAHelper()
        alice = RSAHelper()
        artem = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(1, address=alice.public_key)
        tx0.add_output(1, address=bob.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx0.add_signature(signature, 0)
        tx0.finalize()

        is_tx0_added = blockchain.transaction_add(tx0)
        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()
        is_block1_added = handle_blocks.block_process(block1)


        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(1, address=artem.public_key)
        data_to_sign = tx1.get_data_to_sign(0)
        signature = alice.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()

        is_tx1_added = blockchain.transaction_add(tx1)
        block2 = Block(block1.get_hash(), alice.public_key)
        block2.finalize()
        is_block2_added = handle_blocks.block_process(block2)


        tx2 = Transaction()
        tx2.add_input(tx0.get_hash(), 1)
        tx2.add_output(1, address=artem.public_key)
        data_to_sign = tx2.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx2.add_signature(signature, 0)
        tx2.finalize()

        is_tx2_added = blockchain.transaction_add(tx2)
        block3 = Block(block1.get_hash(), bob.public_key)
        block3.finalize()
        is_block3_added = handle_blocks.block_process(block3)


        tx3 = Transaction()
        tx3.add_input(tx1.get_hash(), 1)
        tx3.add_output(1, address=alice.public_key)
        data_to_sign = tx3.get_data_to_sign(0)
        signature = artem.sign(data_to_sign)
        tx3.add_signature(signature, 0)
        tx3.finalize()

        is_tx3_added = blockchain.transaction_add(tx3)
        block4 = Block(block3.get_hash(), alice.public_key)
        block4.finalize()
        is_block4_added = handle_blocks.block_process(block4)


        self.assertTrue(is_tx0_added, "Tx0 is valid and was processed successfully")
        self.assertTrue(is_tx1_added, "Tx1 is valid and must be processed successfully")
        self.assertTrue(is_tx2_added, "Tx1 is valid and must be processed successfully")
        self.assertFalse(is_tx3_added, "Tx1 is not valid due to usage the utxo from another branch")

        self.assertTrue(is_block1_added, "Block1 was processed successfully")
        self.assertTrue(is_block2_added, "Block2 was processed successfully")
        self.assertTrue(is_block3_added, "Block3 was processed successfully")
        self.assertTrue(is_block4_added, "Block4 was processed successfully")

        self.assertEqual(blockchain.get_block_at_max_height().block, block4, "Block4 must be the head of the blockchain")

        self.assertTrue(block2.get_hash() in blockchain.head_blocks.keys(), "Block2 created new branch with the new tx ")
        self.assertTrue(block4.get_hash() in blockchain.head_blocks.keys(),"Block4 tha leader od the main branch of blockchain")

    # 11
    def test_process_block_utxo_from_parent(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(1, address=alice.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx0.add_signature(signature, 0)
        tx0.finalize()

        is_tx0_added = blockchain.transaction_add(tx0)
        block1 = Block(genesis_block.get_hash(), bob.public_key)
        block1.finalize()
        is_block1_added = handle_blocks.block_process(block1)

        block2 = Block(block1.get_hash(), bob.public_key)
        block2.finalize()
        is_block2_added = handle_blocks.block_process(block2)

        # get the utxo from the tx0 which is in the block1
        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(1, address=bob.public_key)
        data_to_sign = tx1.get_data_to_sign(0)
        signature = alice.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()

        is_tx1_added = blockchain.transaction_add(tx1)
        block3 = Block(block2.get_hash(), bob.public_key)
        block3.finalize()
        is_block3_added = handle_blocks.block_process(block3)

        self.assertTrue(is_tx0_added, "Tx0 is valid and was processed successfully")
        self.assertTrue(is_tx1_added, "Tx1 is valid and must be processed successfully")

        self.assertTrue(is_block1_added, "Block1 was processed successfully")
        self.assertTrue(is_block2_added, "Block2 was processed successfully")
        self.assertTrue(is_block3_added, "Block3 was processed successfully")

        self.assertTrue(tx0 in block1.get_transactions(), "Tx0 is in the block1")
        self.assertTrue(tx1 in block3.get_transactions(), "Tx0 is in the block3")

        self.assertEqual(blockchain.get_block_at_max_height().block, block3, "Block3 must be the head of the blockchain")

        self.assertTrue(block3.get_hash() in blockchain.head_blocks.keys(), "Block2 created new branch with the new tx ")

    # 12
    def test_process_linear_blocks(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()

        block2 = Block(block1.get_hash(), alice.public_key)
        block2.finalize()

        block3 = Block(block2.get_hash(), alice.public_key)
        block3.finalize()

        block4 = Block(block3.get_hash(), alice.public_key)
        block4.finalize()

        is_block1_added = handle_blocks.block_process(block1)
        is_block2_added = handle_blocks.block_process(block2)
        is_block3_added = handle_blocks.block_process(block3)
        is_block4_added = handle_blocks.block_process(block4)

        self.assertTrue(is_block1_added, "Block1 without transaction was processed successfully on genesis")
        self.assertTrue(is_block2_added, "Block2 without transaction was processed successfully on genesis")
        self.assertTrue(is_block3_added, "Block3 without transaction was processed successfully on genesis")
        self.assertTrue(is_block4_added, "Block4 without transaction was processed successfully on genesis")

        self.assertEqual(blockchain.get_block_at_max_height().block, block4, "Block4 must be the head of the blockchain")

        self.assertFalse(block1.get_hash() in blockchain.head_blocks.keys(), "Block1 without transaction was processed successfully directly on genesis / height 1")
        self.assertFalse(block2.get_hash() in blockchain.head_blocks.keys(), "Block2 without transaction was processed successfully directly on genesis / height 2")
        self.assertFalse(block3.get_hash() in blockchain.head_blocks.keys(), "Block3 without transaction was processed successfully directly on genesis / height 3")
        self.assertTrue(block4.get_hash() in blockchain.head_blocks.keys(), "Block4 without transaction was processed successfully directly on genesis / height 4")

    # 13
    def test_process_linear_blocks_cut_of_age(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()

        block2 = Block(block1.get_hash(), alice.public_key)
        block2.finalize()

        block3 = Block(block2.get_hash(), alice.public_key)
        block3.finalize()

        block4 = Block(block3.get_hash(), alice.public_key)
        block4.finalize()

        block5 = Block(block4.get_hash(), alice.public_key)
        block5.finalize()

        block6 = Block(block5.get_hash(), alice.public_key)
        block6.finalize()

        block7 = Block(block6.get_hash(), alice.public_key)
        block7.finalize()

        block8 = Block(block7.get_hash(), alice.public_key)
        block8.finalize()

        block9 = Block(block8.get_hash(), alice.public_key)
        block9.finalize()

        block10 = Block(block9.get_hash(), alice.public_key)
        block10.finalize()

        block11 = Block(block10.get_hash(), alice.public_key)
        block11.finalize()

        block12 = Block(block11.get_hash(), alice.public_key)
        block12.finalize()

        block_on_genesis = Block(genesis_block.get_hash(), alice.public_key)
        block_on_genesis.finalize()


        print("HEIGHT GENESIS:", blockchain.newest_block_node.height)

        is_block1_added = handle_blocks.block_process(block1)
        is_block2_added = handle_blocks.block_process(block2)
        is_block3_added = handle_blocks.block_process(block3)
        is_block4_added = handle_blocks.block_process(block4)
        is_block5_added = handle_blocks.block_process(block5)
        is_block6_added = handle_blocks.block_process(block6)
        is_block7_added = handle_blocks.block_process(block7)
        is_block8_added = handle_blocks.block_process(block8)
        is_block9_added = handle_blocks.block_process(block9)
        is_block10_added = handle_blocks.block_process(block10)
        is_block11_added = handle_blocks.block_process(block11)
        is_block12_added = handle_blocks.block_process(block12)
        is_block_on_genesis_added = handle_blocks.block_process(block_on_genesis)

        print("HEIGHT FINAL:", blockchain.newest_block_node.height)



        self.assertTrue(is_block1_added, "Block1 without transaction was processed successfully")
        self.assertTrue(is_block2_added, "Block2 without transaction was processed successfully")
        self.assertTrue(is_block3_added, "Block3 without transaction was processed successfully")
        self.assertTrue(is_block4_added, "Block4 without transaction was processed successfully")
        self.assertTrue(is_block5_added, "Block5 without transaction was processed successfully")
        self.assertTrue(is_block6_added, "Block6 without transaction was processed successfully")
        self.assertTrue(is_block7_added, "Block7 without transaction was processed successfully")
        self.assertTrue(is_block8_added, "Block8 without transaction was processed successfully")
        self.assertTrue(is_block9_added, "Block9 without transaction was processed successfully")
        self.assertTrue(is_block10_added, "Block10 without transaction was processed successfully")
        self.assertTrue(is_block11_added, "Block11 without transaction was processed successfully")
        self.assertTrue(is_block12_added, "Block12 without transaction was processed successfully")
        self.assertTrue(is_block_on_genesis_added, "Block on genesis without transaction was processed successfully on genesis")

        self.assertEqual(blockchain.get_block_at_max_height().block, block12, "Block12 must be the head of the blockchain")

        self.assertFalse(block11.get_hash() in blockchain.head_blocks.keys(), "Block2 without transaction was processed successfully directly on genesis / height 2")
        self.assertTrue(block_on_genesis.get_hash() in blockchain.head_blocks.keys(), "Block3 without transaction was processed successfully directly on genesis / height 3")
        self.assertTrue(block12.get_hash() in blockchain.head_blocks.keys(), "Block4 without transaction was processed successfully directly on genesis / height 4")

    # 14
    def test_process_linear_blocks_cut_of_age_plus_one(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()

        block2 = Block(block1.get_hash(), alice.public_key)
        block2.finalize()

        block3 = Block(block2.get_hash(), alice.public_key)
        block3.finalize()

        block4 = Block(block3.get_hash(), alice.public_key)
        block4.finalize()

        block5 = Block(block4.get_hash(), alice.public_key)
        block5.finalize()

        block6 = Block(block5.get_hash(), alice.public_key)
        block6.finalize()

        block7 = Block(block6.get_hash(), alice.public_key)
        block7.finalize()

        block8 = Block(block7.get_hash(), alice.public_key)
        block8.finalize()

        block9 = Block(block8.get_hash(), alice.public_key)
        block9.finalize()

        block10 = Block(block9.get_hash(), alice.public_key)
        block10.finalize()

        block11 = Block(block10.get_hash(), alice.public_key)
        block11.finalize()

        block12 = Block(block11.get_hash(), alice.public_key)
        block12.finalize()

        block13 = Block(block12.get_hash(), alice.public_key)
        block13.finalize()


        block_on_genesis = Block(genesis_block.get_hash(), alice.public_key)
        block_on_genesis.finalize()


        is_block1_added = handle_blocks.block_process(block1)
        is_block2_added = handle_blocks.block_process(block2)
        is_block3_added = handle_blocks.block_process(block3)
        is_block4_added = handle_blocks.block_process(block4)
        is_block5_added = handle_blocks.block_process(block5)
        is_block6_added = handle_blocks.block_process(block6)
        is_block7_added = handle_blocks.block_process(block7)
        is_block8_added = handle_blocks.block_process(block8)
        is_block9_added = handle_blocks.block_process(block9)
        is_block10_added = handle_blocks.block_process(block10)
        is_block11_added = handle_blocks.block_process(block11)
        is_block12_added = handle_blocks.block_process(block12)
        is_block13_added = handle_blocks.block_process(block13)
        is_block_on_genesis_added = handle_blocks.block_process(block_on_genesis)

        self.assertTrue(is_block1_added, "Block1 without transaction was processed successfully")
        self.assertTrue(is_block2_added, "Block2 without transaction was processed successfully")
        self.assertTrue(is_block3_added, "Block3 without transaction was processed successfully")
        self.assertTrue(is_block4_added, "Block4 without transaction was processed successfully")
        self.assertTrue(is_block5_added, "Block5 without transaction was processed successfully")
        self.assertTrue(is_block6_added, "Block6 without transaction was processed successfully")
        self.assertTrue(is_block7_added, "Block7 without transaction was processed successfully")
        self.assertTrue(is_block8_added, "Block8 without transaction was processed successfully")
        self.assertTrue(is_block9_added, "Block9 without transaction was processed successfully")
        self.assertTrue(is_block10_added, "Block10 without transaction was processed successfully")
        self.assertTrue(is_block11_added, "Block11 without transaction was processed successfully")
        self.assertTrue(is_block12_added, "Block12 without transaction was processed successfully")
        self.assertTrue(is_block13_added, "Block13 without transaction was processed successfully")
        self.assertFalse(is_block_on_genesis_added, "Block on genesis without transaction is out of the valid cut off age")

        self.assertEqual(blockchain.get_block_at_max_height().block, block13, "Block12 must be the head of the blockchain")

        self.assertFalse(block11.get_hash() in blockchain.head_blocks.keys(), "Block11 was updated with block 12")
        self.assertFalse(block_on_genesis.get_hash() in blockchain.head_blocks.keys(), "Block on genesis was not added")
        self.assertTrue(block13.get_hash() in blockchain.head_blocks.keys(), "Block12 without transaction was processed successfully and is the header of main branch / height 14")

    # 15
    def test_create_block_without_transaction(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        block1 = handle_blocks.block_create(alice.public_key)

        self.assertTrue(block1 is not None, "Block1 without transaction was processed successfully")
        self.assertEqual(blockchain.get_block_at_max_height().block, block1, "Block1 must be the head of the blockchain")
        self.assertTrue(block1.prev_block_hash == genesis_block.get_hash(), "Previous hash of block1 must be the hash of genesis block")

    # 16
    def test_create_block_with_one_valid_transaction(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        tx0 = Transaction()

        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(1, address=alice.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx0.add_signature(signature, 0)
        tx0.finalize()

        blockchain.transaction_add(tx0)

        block1 = handle_blocks.block_create(alice.public_key)

        utxo_pool = blockchain.get_utxo_pool_at_max_height()
        spent_utxo = UTXO(genesis_block.coinbase.get_hash(), 0)
        new_utxo = UTXO(tx0.get_hash(), 0)


        self.assertIn(tx0, block1.get_transactions(), "Transaction must be in new block")
        self.assertTrue(block1 is not None, "Block1 with one valid transaction was processed successfully")
        self.assertEqual(blockchain.get_block_at_max_height().block, block1, "Block1 must be the head of the blockchain")
        self.assertTrue(block1.prev_block_hash == genesis_block.get_hash(), "Previous hash of block1 must be the hash of genesis block")
        self.assertFalse(utxo_pool.contains(spent_utxo), "Used UTXO must be removed")
        self.assertTrue(utxo_pool.contains(new_utxo), "New UTXO must be in new group")

    # 17
    def test_create_block_after_block_with_valid_tx(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        tx0 = Transaction()

        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(1, address=alice.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx0.add_signature(signature, 0)
        tx0.finalize()

        blockchain.transaction_add(tx0)

        block1 = handle_blocks.block_create(alice.public_key)
        block2 = handle_blocks.block_create(alice.public_key)

        utxo_pool = blockchain.get_utxo_pool_at_max_height()
        spent_utxo = UTXO(genesis_block.coinbase.get_hash(), 0)
        new_utxo = UTXO(tx0.get_hash(), 0)


        self.assertIn(tx0, block1.get_transactions(), "Transaction must be in new block")
        self.assertTrue(block1 is not None, "Block1 with one valid transaction was processed successfully")
        self.assertTrue(block2 is not None, "Block2 without transaction was processed successfully")
        self.assertEqual(blockchain.get_block_at_max_height().block, block2, "Block1 must be the head of the blockchain")
        self.assertTrue(block1.prev_block_hash == genesis_block.get_hash(), "Previous hash of block1 must be the hash of genesis block")
        self.assertTrue(block2.prev_block_hash == block1.get_hash(), "Previous hash of block2 must be the hash of block1")
        self.assertFalse(utxo_pool.contains(spent_utxo), "Used UTXO must be removed")
        self.assertTrue(utxo_pool.contains(new_utxo), "New UTXO must be in new group")

    # 18
    def test_create_block_with_transaction_already_in_longest_chain(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(1, address=alice.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx0.add_signature(signature, 0)
        tx0.finalize()

        is_tx0_added = blockchain.transaction_add(tx0)
        block1 = handle_blocks.block_create(alice.public_key)

        is_tx0_added_2 = blockchain.transaction_add(tx0)
        block2 = handle_blocks.block_create(alice.public_key)

        self.assertTrue(is_tx0_added, "Tx0 must be added to the block1")
        self.assertFalse(is_tx0_added_2, "Duplicated Tx0 can not be added to the block1")
        self.assertIn(tx0, block1.get_transactions(), "Transaction0 should be reprocessed in block1")
        self.assertNotIn(tx0, block2.get_transactions(), "Duplicate transaction should not be reprocessed in new block")
        self.assertEqual(block2.prev_block_hash, block1.get_hash(), "Block2's previous hash must be block1's hash")
        self.assertEqual(blockchain.get_block_at_max_height().block, block2, "Block2 must be the head of the blockchain")

    # 19
    def test_create_block_with_double_spending_transaction(self):
        bob = RSAHelper()
        alice = RSAHelper()
        charlie = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(1, address=alice.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx0.add_signature(signature, 0)
        tx0.finalize()

        is_tx0_added = blockchain.transaction_add(tx0)
        block1 = handle_blocks.block_create(alice.public_key)

        # create second tx with the used utxo
        tx1 = Transaction()
        tx1.add_input(genesis_block.get_coinbase().get_hash(), 0)  # repeated usage of utxo
        tx1.add_output(1, address=charlie.public_key)
        data_to_sign1 = tx1.get_data_to_sign(0)
        signature1 = bob.sign(data_to_sign1)
        tx1.add_signature(signature1, 0)
        tx1.finalize()

        is_tx1_added = blockchain.transaction_add(tx1)
        block2 = handle_blocks.block_create(charlie.public_key)

        self.assertTrue(is_tx0_added, "Tx0 must be added to the block1")
        self.assertFalse(is_tx1_added, "Duplicated Tx1 can not be added to the block1")
        self.assertIn(tx0, block1.get_transactions(), "Transaction0 should be reprocessed in block1")
        self.assertNotIn(tx1, block2.get_transactions(), "Duplicate transaction should not be reprocessed in new block")
        self.assertEqual(block2.prev_block_hash, block1.get_hash(), "Block2's previous hash must be block1's hash")
        self.assertEqual(blockchain.get_block_at_max_height().block, block2,"Block2 must be the head of the blockchain")

    # 20
    def test_create_block_with_valid_new_transaction_not_in_any_block(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(3, address=alice.public_key)
        data_to_sign_tx0 = tx0.get_data_to_sign(0)
        signature_tx0 = bob.sign(data_to_sign_tx0)
        tx0.add_signature(signature_tx0, 0)
        tx0.finalize()

        blockchain.transaction_add(tx0)
        block1 = handle_blocks.block_create(alice.public_key)

        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(3, address=bob.public_key)
        data_to_sign_tx1 = tx1.get_data_to_sign(0)
        signature_tx1 = alice.sign(data_to_sign_tx1)
        tx1.add_signature(signature_tx1, 0)
        tx1.finalize()

        blockchain.transaction_add(tx1)
        block2 = handle_blocks.block_create(bob.public_key)

        self.assertIsNotNone(block1, "Block1 should be created successfully")
        self.assertIn(tx0, block1.get_transactions(), "tx0 must be included in block1")
        self.assertIsNotNone(block2, "Block2 should be created successfully")
        self.assertIn(tx1, block2.get_transactions(), "New valid transaction must be included in block2")
        self.assertEqual(block2.prev_block_hash, block1.get_hash(),"block2 previous hash is the hash of block1")
        self.assertEqual(blockchain.get_block_at_max_height().block, block2,"block2 must be the leader of the blockchain")
        utxo_pool = blockchain.get_utxo_pool_at_max_height()
        spent_utxo_for_tx1 = UTXO(tx0.get_hash(), 0)
        new_utxo_for_tx1 = UTXO(tx1.get_hash(), 0)
        self.assertFalse(utxo_pool.contains(spent_utxo_for_tx1),"used utxo can not be in the utxo_pool")
        self.assertTrue(utxo_pool.contains(new_utxo_for_tx1),"new utxo must appear in utxo pool")

    # 21
    def test_create_block_after_invalid_transaction(self):
        bob = RSAHelper()
        alice = RSAHelper()
        charlie = RSAHelper()
        dima = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(1, address=alice.public_key)
        tx0.add_output(1, address=charlie.public_key)
        tx0.add_output(1, address=dima.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        signature = bob.sign(data_to_sign)
        tx0.add_signature(signature, 0)
        tx0.finalize()

        is_tx0_added = blockchain.transaction_add(tx0)
        block1 = handle_blocks.block_create(alice.public_key)

        # create second tx with the used utxo
        tx1 = Transaction()
        tx1.add_input(genesis_block.get_coinbase().get_hash(), 0)  # repeated usage of utxo
        tx1.add_output(1, address=charlie.public_key)
        data_to_sign1 = tx1.get_data_to_sign(0)
        signature1 = bob.sign(data_to_sign1)
        tx1.add_signature(signature1, 0)
        tx1.finalize()

        # create tx with the output > input
        tx2 = Transaction()
        tx2.add_input(tx0.get_hash(), 0)
        tx2.add_output(2, address=charlie.public_key) # input 1.0 / output 2.0
        data_to_sign1 = tx2.get_data_to_sign(0)
        signature1 = alice.sign(data_to_sign1)
        tx2.add_signature(signature1, 0)
        tx2.finalize()

        # create tx with invalid signature
        tx3 = Transaction()
        tx3.add_input(tx0.get_hash(), 1)
        tx3.add_output(2, address=bob.public_key)
        data_to_sign1 = tx3.get_data_to_sign(0)
        signature1 = charlie.sign(data_to_sign1)
        invalidate_signature = bytearray(signature1)  # Create invalid signature
        invalidate_signature[-1] ^= 0x01
        invalidate_signature = bytes(invalidate_signature)
        tx3.add_signature(invalidate_signature, 0)
        tx3.finalize()

        is_tx1_added = blockchain.transaction_add(tx1)
        is_tx2_added = blockchain.transaction_add(tx2)
        is_tx3_added = blockchain.transaction_add(tx3)
        block2 = handle_blocks.block_create(charlie.public_key)

        self.assertTrue(is_tx0_added, "Tx0 must be added to the block1")
        self.assertFalse(is_tx1_added, "Duplicated Tx1 can not be added to the block2")
        self.assertFalse(is_tx2_added, "Output more than input Tx2 can not be added to the block2")
        self.assertFalse(is_tx3_added, "Invalid signature Tx3 can not be added to the block1")
        self.assertIn(tx0, block1.get_transactions(), "Transaction0 should be reprocessed in block1")
        self.assertNotIn(tx1, block2.get_transactions(), "Tx1 should not be reprocessed in new block")
        self.assertNotIn(tx2, block2.get_transactions(), "Tx2 should not be reprocessed in new block")
        self.assertNotIn(tx3, block2.get_transactions(), "Tx3 should not be reprocessed in new block")
        self.assertEqual(block2.prev_block_hash, block1.get_hash(), "Block2's previous hash must be block1's hash")
        self.assertEqual(blockchain.get_block_at_max_height().block, block2,"Block2 must be the head of the blockchain")

    # 22
    def test_create_tx_block_tx_block(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(3, address=alice.public_key)
        data_to_sign_tx0 = tx0.get_data_to_sign(0)
        signature_tx0 = bob.sign(data_to_sign_tx0)
        tx0.add_signature(signature_tx0, 0)
        tx0.finalize()

        blockchain.transaction_add(tx0)
        block1 = handle_blocks.block_create(bob.public_key)

        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(3, address=bob.public_key)
        data_to_sign_tx1 = tx1.get_data_to_sign(0)
        signature_tx1 = alice.sign(data_to_sign_tx1)
        tx1.add_signature(signature_tx1, 0)
        tx1.finalize()

        blockchain.transaction_add(tx1)
        block2 = handle_blocks.block_create(bob.public_key)

        self.assertIsNotNone(block1, "Block1 should be created successfully")
        self.assertIn(tx0, block1.get_transactions(), "tx0 must be included in block1")

        self.assertIsNotNone(block2, "Block2 should be created successfully")
        self.assertIn(tx1, block2.get_transactions(), "New valid transaction must be included in block2")

        self.assertEqual(block2.prev_block_hash, block1.get_hash(),"block2 previous hash is the hash of block1")
        self.assertEqual(blockchain.get_block_at_max_height().block, block2,"block2 must be the leader of the blockchain")

        utxo_pool = blockchain.get_utxo_pool_at_max_height()
        spent_utxo_for_tx1 = UTXO(tx0.get_hash(), 0)
        new_utxo_for_tx1 = UTXO(tx1.get_hash(), 0)
        self.assertFalse(utxo_pool.contains(spent_utxo_for_tx1),"used utxo can not be in the utxo_pool")
        self.assertTrue(utxo_pool.contains(new_utxo_for_tx1),"new utxo must appear in utxo pool")

    # 23
    def test_create_tx_block_tx_block_on_prev(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(3, address=alice.public_key)
        data_to_sign_tx0 = tx0.get_data_to_sign(0)
        signature_tx0 = bob.sign(data_to_sign_tx0)
        tx0.add_signature(signature_tx0, 0)
        tx0.finalize()

        blockchain.transaction_add(tx0)
        block1 = handle_blocks.block_create(bob.public_key)

        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(3, address=bob.public_key)
        data_to_sign_tx1 = tx1.get_data_to_sign(0)
        signature_tx1 = alice.sign(data_to_sign_tx1)
        tx1.add_signature(signature_tx1, 0)
        tx1.finalize()

        blockchain.transaction_add(tx1)
        block2 = Block(block1.get_hash(), alice.public_key)
        block2.finalize()
        is_block2_added = handle_blocks.block_process(block2)

        self.assertIsNotNone(block1, "Block1 should be created successfully")
        self.assertIn(tx0, block1.get_transactions(), "tx0 must be included in block1")

        self.assertTrue(is_block2_added, "Block2 should be created successfully")
        self.assertIn(tx1, block2.get_transactions(), "New valid transaction must be included in block2")

        self.assertEqual(block2.prev_block_hash, block1.get_hash(),"block2 previous hash is the hash of block1")
        self.assertEqual(blockchain.get_block_at_max_height().block, block2,"block2 must be the leader of the blockchain")

        utxo_pool = blockchain.get_utxo_pool_at_max_height()
        spent_utxo_for_tx1 = UTXO(tx0.get_hash(), 0)
        new_utxo_for_tx1 = UTXO(tx1.get_hash(), 0)
        self.assertFalse(utxo_pool.contains(spent_utxo_for_tx1),"used utxo can not be in the utxo_pool")
        self.assertTrue(utxo_pool.contains(new_utxo_for_tx1),"new utxo must appear in utxo pool")

    # 24
    def test_create_tx_block_tx_proccess_tx_from_another_branch(self):
        bob = RSAHelper()
        alice = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(3, address=alice.public_key)
        data_to_sign_tx0 = tx0.get_data_to_sign(0)
        signature_tx0 = bob.sign(data_to_sign_tx0)
        tx0.add_signature(signature_tx0, 0)
        tx0.finalize()

        is_tx0_added = blockchain.transaction_add(tx0)
        block1 = handle_blocks.block_create(bob.public_key)


        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(3, address=bob.public_key)
        data_to_sign_tx1 = tx1.get_data_to_sign(0)
        signature_tx1 = alice.sign(data_to_sign_tx1)
        tx1.add_signature(signature_tx1, 0)
        tx1.finalize()

        is_tx1_added = blockchain.transaction_add(tx1)
        block2 = Block(genesis_block.get_hash(), alice.public_key)
        block2.finalize()
        is_block2_added = handle_blocks.block_process(block2)



        self.assertTrue(is_tx0_added, "Tx0 should be created successfully")
        self.assertTrue(is_tx1_added, "Tx1 should be created successfully")

        self.assertEqual(blockchain.get_block_at_max_height().block, block1,"block1 must be the leader of the blockchain")
        self.assertFalse(is_block2_added, "Block was not created because block has the invalid tx (Tx is valid but use the utxo from another branch)")

        self.assertIn(tx0, block1.get_transactions(), "tx0 must be included in block1")

        self.assertEqual(block1.prev_block_hash, genesis_block.get_hash(),"block1 previous hash is the hash of genesis block")

        self.assertTrue(block1.get_hash() in blockchain.get_head_blocks().keys(),"block1 the leader of first branch")

        utxo_pool = blockchain.get_utxo_pool_at_max_height()
        utxo_from_tx0 = UTXO(tx0.get_hash(), 0)
        self.assertTrue(utxo_pool.contains(utxo_from_tx0),"utxo was not used so must appear in utxo pool")

    # 25
    def test_process_blocks_on_genesis_create_block(self):
        bob = RSAHelper()
        alice = RSAHelper()
        dima = RSAHelper()
        artem = RSAHelper()
        mark = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()

        block2 = Block(genesis_block.get_hash(), bob.public_key)
        block2.finalize()

        block3 = Block(genesis_block.get_hash(), mark.public_key)
        block3.finalize()

        block4 = Block(genesis_block.get_hash(), dima.public_key)
        block4.finalize()

        is_block1_added = handle_blocks.block_process(block1)
        is_block2_added = handle_blocks.block_process(block2)
        is_block3_added = handle_blocks.block_process(block3)
        is_block4_added = handle_blocks.block_process(block4)

        block5 = handle_blocks.block_create(artem.public_key)


        self.assertTrue(is_block1_added, "Block1 without transaction was processed successfully on genesis")
        self.assertTrue(is_block2_added, "Block2 without transaction was processed successfully on genesis")
        self.assertTrue(is_block3_added, "Block3 without transaction was processed successfully on genesis")
        self.assertTrue(is_block4_added, "Block4 without transaction was processed successfully on genesis")
        self.assertIsNotNone(block5, "Block5 was created successfully")


        self.assertFalse(block1.get_hash() in blockchain.get_head_blocks().keys(), "Block5 on the block1 so block1 is nt the header")
        self.assertTrue(block2.get_hash() in blockchain.get_head_blocks().keys(), "Block2 on genesis is header")
        self.assertTrue(block3.get_hash() in blockchain.get_head_blocks().keys(), "Block3 on genesis is header")
        self.assertTrue(block4.get_hash() in blockchain.get_head_blocks().keys(), "Block4 on genesis is header")
        self.assertTrue(block5.get_hash() in blockchain.get_head_blocks().keys(), "Block5 is the header of the main branch");

        self.assertEqual(blockchain.get_block_at_max_height().block, block5,"block5 must be the leader of the blockchain")

    #26
    def test_process_blocks_on_genesis_correct_create_block(self):
        bob = RSAHelper()
        alice = RSAHelper()
        dima = RSAHelper()
        artem = RSAHelper()
        mark = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        # HEIGHT 1
        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()

        block2 = Block(genesis_block.get_hash(), bob.public_key)
        block2.finalize()

        block3 = Block(genesis_block.get_hash(), mark.public_key)
        block3.finalize()

        # HEIGHT 2
        block4 = Block(block1.get_hash(), dima.public_key)
        block4.finalize()

        block5 = Block(block2.get_hash(), alice.public_key)
        block5.finalize()

        is_block1_added = handle_blocks.block_process(block1)
        is_block2_added = handle_blocks.block_process(block2)
        is_block3_added = handle_blocks.block_process(block3)
        is_block4_added = handle_blocks.block_process(block4)
        is_block5_added = handle_blocks.block_process(block5)

        # Create block on max height in this case create block on block 4
        block_new = handle_blocks.block_create(artem.public_key)

        # we have such branches:
        # g -> 1 -> 4 -> block_new
        # g -> 2 -> 5
        # g -> 3


        self.assertTrue(is_block1_added, "Block1 without transaction was processed successfully on genesis")
        self.assertTrue(is_block2_added, "Block2 without transaction was processed successfully on genesis")
        self.assertTrue(is_block3_added, "Block3 without transaction was processed successfully on genesis")
        self.assertTrue(is_block4_added, "Block4 without transaction was processed successfully on genesis")
        self.assertTrue(is_block5_added, "Block5 without transaction was processed successfully on genesis")
        self.assertIsNotNone(block_new, "Block_new was created successfully")


        self.assertFalse(block1.get_hash() in blockchain.get_head_blocks().keys(), "Block5 on the block1 so block1 is not the header")
        self.assertFalse(block2.get_hash() in blockchain.get_head_blocks().keys(), "Block4 is on the block2, so is not header")
        self.assertTrue(block3.get_hash() in blockchain.get_head_blocks().keys(), "Block3 on genesis is header")
        self.assertFalse(block4.get_hash() in blockchain.get_head_blocks().keys(), "Block_new is in block 4, so block4 is not a header header")
        self.assertTrue(block5.get_hash() in blockchain.get_head_blocks().keys(), "Block5 is the header of one of the branch")
        self.assertTrue(block_new.get_hash() in blockchain.get_head_blocks().keys(), "Block_new is the header of the main branch")

        self.assertEqual(blockchain.get_block_at_max_height().block, block_new,"block5 must be the leader of the blockchain")

    # 27
    def test_process_blocks_outside_cutoff_age(self):
        bob = RSAHelper()
        alice = RSAHelper()
        dima = RSAHelper()

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()

        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        current_parent = genesis_block
        for height in range(1, 14):
            new_block = Block(current_parent.get_hash(), bob.public_key)
            new_block.finalize()

            is_processed = handle_blocks.block_process(new_block)
            self.assertTrue(is_processed, f"Block at height {height} must be processed successfully")
            current_parent = new_block

        # How it looks like now:
        # - maxHeight = 13
        # - CUT_OFF_AGE = 12
        # => блоки на высоте < (13 - 12) = 1 (pruned).
        # Genesis height=0.

        old_block = Block(genesis_block.get_hash(), alice.public_key)
        old_block.finalize()
        is_old_block_added = handle_blocks.block_process(old_block)

        new_valid_block = handle_blocks.block_create(dima.public_key)

        self.assertFalse(is_old_block_added,"Block whose parent is outside (maxHeight - CUT_OFF_AGE) must not be accepted")
        self.assertNotIn(old_block.get_hash(), blockchain.get_head_blocks().keys(),"Old block must not appear in the set of head blocks")

        self.assertIsNotNone(new_valid_block, "New block on top of the max height must be accepted")
        self.assertIn(new_valid_block.get_hash(), blockchain.get_head_blocks().keys(),"New valid block must be one of the chain heads")

        self.assertEqual(blockchain.get_block_at_max_height().block, new_valid_block,"The new valid block should become the tip of the longest chain")

    #Multisig
    # 1
    def test_create_multisig_address(self):
        pool = UTXOPool()
        all_txs = []

        artem = RSAHelper()
        alice = RSAHelper()
        bob = RSAHelper()
        dima = RSAHelper()

        tx0 = Transaction()
        tx0.add_output(20.0, artem.public_key)
        tx0.finalize()

        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(20.0, multisig_keys = [alice.public_key, bob.public_key, dima.public_key], required=2)
        data_to_sign = tx1.get_data_to_sign(0)
        signature = alice.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()

        self.assertIsNotNone(tx1.get_outputs()[0].address, "Tx0 must be created correctly")
        self.assertTrue(tx1.get_outputs()[0].is_multisig, "Output created the multisig address")
        self.assertTrue(2 == tx1.get_outputs()[0].required, "Minimum number to assign is 2")
        self.assertTrue(alice.public_key in tx1.get_outputs()[0].multisig_keys, "alice is one of the member who need to write")
        self.assertTrue(bob.public_key in tx1.get_outputs()[0].multisig_keys, "bob is one of the member who need to write")
        self.assertTrue(dima.public_key in tx1.get_outputs()[0].multisig_keys, "dima is one of the member who need to write")



