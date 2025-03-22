import unittest
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

        genesis_block = Block(None, bob.public_key)
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()

        block2 = Block(genesis_block.get_hash(), alice.public_key)
        block2.finalize()

        block3 = Block(genesis_block.get_hash(), alice.public_key)
        block3.finalize()

        block4 = Block(genesis_block.get_hash(), alice.public_key)
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

        self.assertTrue(block1.get_hash() in blockchain.head_blocks.keys(), "Block1 without transaction was processed successfully directly on genesis / height 1")
        self.assertTrue(block2.get_hash() in blockchain.head_blocks.keys(), "Block2 without transaction was processed successfully directly on genesis / height 1")
        self.assertTrue(block3.get_hash() in blockchain.head_blocks.keys(), "Block3 without transaction was processed successfully directly on genesis / height 1")
        self.assertTrue(block4.get_hash() in blockchain.head_blocks.keys(), "Block4 without transaction was processed successfully directly on genesis / height 1")

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
