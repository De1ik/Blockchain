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

        # genesis_block.coinbase.get_hash()
        utxo_pool = blockchain.get_utxo_pool_at_max_height()
        # print('pool:', utxo_pool.get_tx_output(utxo_pool.get_all_utxo()[0]).deserialize_key(utxo_pool.get_tx_output(utxo_pool.get_all_utxo()[0]).address))
        # print('genesis_block:', genesis_block.get_coinbase().get_outputs()[0].deserialize_key(utxo_pool.get_tx_output(utxo_pool.get_all_utxo()[0]).address))

        tx0 = Transaction()
        tx0.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx0.add_output(1, address=alice.public_key)
        data_to_sign = tx0.get_data_to_sign(0)
        # print("Test_data_to_sign:", data_to_sign)
        signature = bob.sign(data_to_sign)
        # print("TEst_Signature:", signature)
        tx0.add_signature(signature, 0)
        tx0.finalize()
        # print("TEst_PBKEY:", (genesis_block.get_coinbase().get_outputs()[0].deserialize_key(genesis_block.get_coinbase().get_outputs()[0].address)).public_numbers())
        #

        if not blockchain.transaction_add(tx0):
            print('was not added to the blockchain')
        else:
            print('blockchain has new tx')



        print(blockchain.get_transaction_pool().get_transactions())

        block1 = Block(genesis_block.get_hash(), alice.public_key)
        block1.finalize()

        result = handle_blocks.block_process(block1)
        print(result)
        # #
        # # utxo_pool = blockchain.get_utxo_pool_at_max_height()
        # # spent_utxo = genesis_block.get_hash(), 0
        # # new_utxo = tx0.get_hash(), 0
        #
        # print(block1.get_transactions())

        # self.assertTrue(result, "Block without transaction was processed successfully")
        # self.assertEqual(blockchain.get_block_at_max_height().block, block1, "Block must be the head of the blockchain")
        # self.assertIn(tx0, block1.get_transactions(), "Транзакция должна быть в новом блоке")
        # self.assertFalse(utxo_pool.contains(spent_utxo), "Потраченный UTXO должен исчезнуть из пула")
        # self.assertTrue(utxo_pool.contains(new_utxo), "Новый UTXO должен появиться в пуле")


    # def test_tx_validator_with_valid_transaction(self):
    #     # 1. Create an empty UTXOPool.
    #     pool = UTXOPool()
    #
    #     # 2. Create a key pair.
    #     rsa_helper = RSAHelper()
    #     rsa_helper_1 = RSAHelper()
    #     rsa_helper_2 = RSAHelper()
    #     rsa_helper_3 = RSAHelper()
    #
    #     rsa_helper_x = RSAHelper()
    #
    #     # 3. Create a base transaction (tx0) that produces an output worth 10 coins.
    #     tx0 = Transaction()
    #     tx0.add_output(5.0, rsa_helper.public_key)
    #     tx0.finalize()
    #
    #     # 4. Insert tx0’s output into the UTXOPool.
    #     utxo0 = UTXO(tx0.get_hash(), 0)
    #     pool.add_utxo(utxo0, tx0.get_output(0))
    #
    #     # 5. Create a new transaction (tx1) that spends tx0's output.
    #     tx1 = Transaction()
    #     tx1.add_input(tx0.get_hash(), 0)
    #     tx1.add_output(5.0, multisig_keys = [rsa_helper_1.public_key, rsa_helper_2.public_key, rsa_helper_3.public_key], required=3)
    #     data_to_sign = tx1.get_data_to_sign(0)
    #     signature = rsa_helper.sign(data_to_sign)
    #     tx1.add_signature(signature, 0)
    #     tx1.finalize()
    #
    #     utxo0 = UTXO(tx1.get_hash(), 0)
    #     pool.add_utxo(utxo0, tx1.get_output(0))
    #
    #     tx2 = Transaction()
    #     tx2.add_input(tx1.get_hash(), 0)
    #     tx2.add_output(5.0, address=rsa_helper.public_key)
    #
    #     data_to_sign = tx2.get_data_to_sign(0)
    #
    #     signature1 = rsa_helper_1.sign(data_to_sign)
    #     tx2.add_signature(signature1, 0)
    #
    #     signature2 = rsa_helper_2.sign(data_to_sign)
    #     tx2.add_signature(signature2, 0)
    #
    #     signature3 = rsa_helper_3.sign(data_to_sign)
    #     tx2.add_signature(signature3, 0)
    #
    #     tx2.finalize()
    #
    #     utxo0 = UTXO(tx2.get_hash(), 0)
    #     pool.add_utxo(utxo0, tx2.get_output(0))
    #
    #
    #     tx3 = Transaction()
    #     tx3.add_input(tx2.get_hash(), 0)
    #     tx3.add_output(5.0, address=rsa_helper_x.public_key)
    #
    #     data_to_sign = tx3.get_data_to_sign(0)
    #
    #     signature = rsa_helper.sign(data_to_sign)
    #     tx3.add_signature(signature, 0)
    #     tx3.finalize()
    #
    #
    #     # 6. Create the handler and validate the transaction.
    #     handler = HandleTxs(pool)
    #     valid = handler.txIsValid(tx3)
    #     self.assertTrue(valid, "Transaction tx1 should be valid with properly signed inputs and valid UTXOs.")
