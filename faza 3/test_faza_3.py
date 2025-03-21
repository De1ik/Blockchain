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