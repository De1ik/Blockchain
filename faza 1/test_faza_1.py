import unittest
from  rsa import RSA
from Transaction import Transaction
from UTXO import UTXO
from UTXOPool import UTXOPool
from HandleTxs import HandleTxs
from MaxFeeHandleTxs import MaxFeeHandleTxs


class HandleTxsTest(unittest.TestCase):
    # 1
    def test_tx_validator_with_valid_transaction(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()

        # 2. Create a key pair.
        rsa_helper = RSA.RSAHelper()
        rsa_helper_2 = RSA.RSAHelper()

        # 3. Create a base transaction (tx0) that produces an output worth 10 coins.
        tx0 = Transaction()
        tx0.add_output(10.0, rsa_helper.public_key)
        tx0.finalize()

        # 4. Insert tx0’s output into the UTXOPool.
        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        # 5. Create a new transaction (tx1) that spends tx0's output.
        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(5.0, rsa_helper.public_key)
        tx1.add_output(3.0, rsa_helper_2.public_key)
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()


        # 6. Create the handler and validate the transaction.
        handler = HandleTxs(pool)
        valid = handler.txIsValid(tx1)
        self.assertTrue(valid, "Transaction tx1 should be valid with properly signed inputs and valid UTXOs.")

    # 2
    def test_tx_validator_with_incorrect_signature(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()
        # Create a key pair.
        rsa_helper = RSA.RSAHelper()

        # 3. Create a base transaction (tx0) that produces an output worth 10 coins.
        tx0 = Transaction()
        tx0.add_output(10.0, rsa_helper.public_key)
        tx0.finalize()
        # 4. Insert tx0’s output into the UTXOPool.
        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        # 5. Create a new transaction (tx1) that spends tx0's output.
        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(5.0, rsa_helper.public_key)
        tx1.add_output(4.0, rsa_helper.public_key)  # Total outputs = 9.0, fee = 1.0

        # 6. Sign tx1’s input.
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper.sign(data_to_sign)

        invalid_sig = bytearray(signature)
        invalid_sig[-1] ^= 0x01
        invalid_sig = bytes(invalid_sig)

        tx1.add_signature(invalid_sig, 0)
        tx1.finalize()

        # 7. Create the handler and validate the transaction.
        handler = HandleTxs(pool)
        valid = handler.txIsValid(tx1)
        self.assertFalse(valid, "Transaction tx1 should be invalid because of the invalid signature.")

    # 3
    def test_tx_validator_with_incorrect_private_key(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()
        # Create a key pair.
        rsa_helper_main = RSA.RSAHelper()
        rsa_helper_another = RSA.RSAHelper()

        # 3. Create a base transaction (tx0) that produces an output worth 10 coins.
        tx0 = Transaction()
        tx0.add_output(10.0, rsa_helper_main.public_key)
        tx0.finalize()
        # 4. Insert tx0’s output into the UTXOPool.
        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        # 5. Create a new transaction (tx1) that spends tx0's output.
        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(5.0, rsa_helper_main.public_key)
        tx1.add_output(4.0, rsa_helper_main.public_key)  # Total outputs = 9.0, fee = 1.0

        # 6. Sign tx1’s input.
        data_to_sign = tx1.get_data_to_sign(0)

        # sign with another private key
        signature = rsa_helper_another.sign(data_to_sign)

        tx1.add_signature(signature, 0)
        tx1.finalize()

        # 7. Create the handler and validate the transaction.
        handler = HandleTxs(pool)
        valid = handler.txIsValid(tx1)
        self.assertFalse(valid, "Transaction tx1 should be invalid because it was sign with another private key.")

    # 4
    def test_tx_validator_input_less_output(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()
        # Create a key pair.
        rsa_helper = RSA.RSAHelper()

        # 3. Create a base transaction (tx0) that produces an output worth 10 coins.
        tx0 = Transaction()
        tx0.add_output(6.0, rsa_helper.public_key)
        tx0.finalize()
        # 4. Insert tx0’s output into the UTXOPool.
        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        # 5. Create a new transaction (tx1) that spends more than has at inputs.
        # Inputs = 6 / Outputs = 9
        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(5.0, rsa_helper.public_key)
        tx1.add_output(4.0, rsa_helper.public_key)  # Total outputs = 9.0, fee = 1.0

        # 6. Sign tx1’s input.
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper.sign(data_to_sign)

        tx1.add_signature(signature, 0)
        tx1.finalize()

        # 7. Create the handler and validate the transaction.
        handler = HandleTxs(pool)
        valid = handler.txIsValid(tx1)
        self.assertFalse(valid, "Transaction tx1 should be invalid because it try to spend more than was received.")

    # 5
    def test_tx_validator_output_out_utx_pool(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()
        # We will add tx0 to the main pool, but for the handler will provide empty pool
        pool_empty = UTXOPool()
        # Create a key pair.
        rsa_helper = RSA.RSAHelper()

        # 3. Create a base transaction (tx0) that produces an output worth 20 coins.
        tx0 = Transaction()
        tx0.add_output(20.0, rsa_helper.public_key)
        tx0.finalize()

        # 4. Insert tx0’s output into the UTXOPool.
        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        # 5. Create a new transaction (tx1) that spends tx0's output.
        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(5.0, rsa_helper.public_key)
        tx1.add_output(4.0, rsa_helper.public_key)  # Total outputs = 9.0, fee = 1.0

        # 6. Sign tx1’s input.
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper.sign(data_to_sign)

        tx1.add_signature(signature, 0)
        tx1.finalize()

        # 7. Create the handler and validate the transaction.
        handler = HandleTxs(pool_empty)
        valid = handler.txIsValid(tx1)
        self.assertFalse(valid, "Transaction tx1 should be invalid because it try to spend UTXO which is not in the pool.")

    # 6
    def test_tx_validator_double_spending(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()

        # Create a key pair.
        rsa_helper = RSA.RSAHelper()

        # 3. Create a base transaction (tx0) that produces an output worth 20 coins.
        tx0 = Transaction()
        tx0.add_output(20.0, rsa_helper.public_key)
        tx0.finalize()

        # 4. Insert tx0’s output into the UTXOPool.
        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        # 5. Create a new transaction (tx1) that spends tx0's output.
        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)

        # Add the same UTXO as an input: double spending
        tx1.add_input(tx0.get_hash(), 0)

        tx1.add_output(5.0, rsa_helper.public_key)
        tx1.add_output(4.0, rsa_helper.public_key)  # Total outputs = 9.0, fee = 1.0

        # 6. Sign tx1’s input.
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()

        # 7. Create the handler and validate the transaction.
        handler = HandleTxs(pool)
        valid = handler.txIsValid(tx1)
        self.assertFalse(valid, "Transaction tx1 should be invalid because of the usage the same UTXO more than one time.")

    # 7
    def test_tx_validator_negative_output(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()

        # Create a key pair.
        rsa_helper = RSA.RSAHelper()

        # 3. Create a base transaction (tx0) that produces an output worth 20 coins.
        tx0 = Transaction()
        tx0.add_output(20.0, rsa_helper.public_key)
        tx0.finalize()

        # 4. Insert tx0’s output into the UTXOPool.
        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        # 5. Create a new transaction (tx1) that spends tx0's output.
        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)

        tx1.add_output(5.0, rsa_helper.public_key)
        # Add negative output which is not valid
        tx1.add_output(-4.0, rsa_helper.public_key)

        # 6. Sign tx1’s input.
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()

        # 7. Create the handler and validate the transaction.
        handler = HandleTxs(pool)
        valid = handler.txIsValid(tx1)
        self.assertFalse(valid, "Transaction tx1 should be invalid because of the negative output.")

    # 8
    def test_tx_handler_all_valid_txs(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()
        all_txs = []

        # Create 3 different pair of public/private keys.
        rsa_helper_1 = RSA.RSAHelper()
        rsa_helper_2 = RSA.RSAHelper()
        rsa_helper_3 = RSA.RSAHelper()

        # 3. Create a base transaction (tx0) that produces an output worth 20 coins.
        tx0 = Transaction()
        tx0.add_output(20.0, rsa_helper_1.public_key)
        tx0.finalize()

        # 4. Insert tx0’s output into the UTXOPool.
        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        # 5. Create a new transaction (tx1) that spends tx0's output.
        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)

        tx1.add_output(7.0, rsa_helper_1.public_key)
        tx1.add_output(5.0, rsa_helper_2.public_key)
        tx1.add_output(3.0, rsa_helper_3.public_key) # Total outputs = 15.0, fee = 5.0

        # 6. Sign tx1’s input.
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper_1.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()


        # New TX
        tx2 = Transaction()
        tx2.add_input(tx1.get_hash(), 1)
        tx2.add_output(2.0, rsa_helper_3.public_key)

        data_to_sign = tx2.get_data_to_sign(0)
        signature = rsa_helper_2.sign(data_to_sign)
        tx2.add_signature(signature, 0)

        tx2.finalize()


        tx3 = Transaction()
        tx3.add_input(tx1.get_hash(), 2)
        tx3.add_output(2.0, rsa_helper_1.public_key)

        # 6. Sign tx1’s input.
        data_to_sign = tx3.get_data_to_sign(0)
        signature = rsa_helper_3.sign(data_to_sign)
        tx3.add_signature(signature, 0)
        tx3.finalize()



        # 8. Create the handler and validate the list of transactions.
        all_txs.append(tx1)
        all_txs.append(tx2)
        all_txs.append(tx3)

        handler = HandleTxs(pool)
        correct_txs = handler.handler(all_txs)

        expected_hashes = [tx.get_hash() for tx in all_txs]
        received_hashes = [tx.get_hash() for tx in correct_txs]

        self.assertEqual(expected_hashes, received_hashes, "List of transactions should be the same length.")
        for i in range(len(expected_hashes)):
            self.assertEqual(received_hashes[i], received_hashes[i], "List of transactions should be valid.")

    # 9
    def test_tx_handler_invalid_due_signature(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()
        all_txs = []

        # Create 3 different pair of public/private keys.
        rsa_helper_1 = RSA.RSAHelper()
        rsa_helper_2 = RSA.RSAHelper()
        rsa_helper_3 = RSA.RSAHelper()

        # 3. Create a base transaction (tx0) that produces an output worth 20 coins.
        tx0 = Transaction()
        tx0.add_output(20.0, rsa_helper_1.public_key)
        tx0.finalize()

        # 4. Insert tx0’s output into the UTXOPool.
        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        # 5. Create a new transaction (tx1) that spends tx0's output.
        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)

        tx1.add_output(7.0, rsa_helper_1.public_key)
        tx1.add_output(5.0, rsa_helper_2.public_key)
        tx1.add_output(3.0, rsa_helper_3.public_key)  # Total outputs = 15.0, fee = 5.0

        # 6. Sign tx1’s input.
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper_1.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()

        # New TX
        tx2 = Transaction()
        tx2.add_input(tx1.get_hash(), 1)
        tx2.add_output(2.0, rsa_helper_3.public_key)

        # create invalid sig
        data_to_sign = tx2.get_data_to_sign(0)
        signature = rsa_helper_2.sign(data_to_sign)
        invalid_sig = bytearray(signature)
        invalid_sig[-1] ^= 0x01
        invalid_sig = bytes(invalid_sig)
        tx2.add_signature(invalid_sig, 0)

        tx2.finalize()

        tx3 = Transaction()
        tx3.add_input(tx1.get_hash(), 2)
        tx3.add_output(2.0, rsa_helper_1.public_key)

        # 6. Sign tx1’s input.
        data_to_sign = tx3.get_data_to_sign(0)
        signature = rsa_helper_3.sign(data_to_sign)
        tx3.add_signature(signature, 0)
        tx3.finalize()

        # 8. Create the handler and validate the list of transactions.
        all_txs.append(tx1)
        all_txs.append(tx2)
        all_txs.append(tx3)

        handler = HandleTxs(pool)
        received_valid_txs = handler.handler(all_txs)
        expected_valid_txs = [tx1, tx3]


        expected_hashes = [tx.get_hash() for tx in expected_valid_txs]
        received_hashes = [tx.get_hash() for tx in received_valid_txs]

        self.assertEqual(len(expected_hashes), len(received_hashes), "List of transactions should be the same length.")
        self.assertEqual(expected_valid_txs, received_valid_txs, "Check valid transaction by hash.")

    # 10
    def test_tx_handler_invalid_due_inp_op(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()
        all_txs = []

        rsa_helper_1 = RSA.RSAHelper()
        rsa_helper_2 = RSA.RSAHelper()
        rsa_helper_3 = RSA.RSAHelper()

        tx0 = Transaction()
        tx0.add_output(20.0, rsa_helper_1.public_key)
        tx0.finalize()

        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(7.0, rsa_helper_1.public_key)
        tx1.add_output(5.0, rsa_helper_2.public_key)
        tx1.add_output(3.0, rsa_helper_3.public_key)  # Total outputs = 15.0, fee = 5.0
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper_1.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()


        tx2 = Transaction()
        tx2.add_input(tx1.get_hash(), 1)

        #Set more output than input (Input 5 / Output 6)
        tx2.add_output(6.0, rsa_helper_3.public_key)
        data_to_sign = tx2.get_data_to_sign(0)
        signature = rsa_helper_2.sign(data_to_sign)
        tx2.add_signature(signature, 0)
        tx2.finalize()

        tx3 = Transaction()
        tx3.add_input(tx1.get_hash(), 2)
        tx3.add_output(2.0, rsa_helper_1.public_key)
        data_to_sign = tx3.get_data_to_sign(0)
        signature = rsa_helper_3.sign(data_to_sign)
        tx3.add_signature(signature, 0)
        tx3.finalize()

        all_txs.append(tx1)
        all_txs.append(tx2)
        all_txs.append(tx3)

        handler = HandleTxs(pool)
        received_valid_txs = handler.handler(all_txs)
        expected_valid_txs = [tx1, tx3]


        expected_hashes = [tx.get_hash() for tx in expected_valid_txs]
        received_hashes = [tx.get_hash() for tx in received_valid_txs]

        self.assertEqual(len(expected_hashes), len(received_hashes), "List of transactions should be the same length.")
        self.assertEqual(expected_valid_txs, received_valid_txs, "Check valid transaction by hash.")

    # 11
    def test_tx_handler_invalid_due_double_spending(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()
        all_txs = []

        rsa_helper_1 = RSA.RSAHelper()
        rsa_helper_2 = RSA.RSAHelper()
        rsa_helper_3 = RSA.RSAHelper()

        tx0 = Transaction()
        tx0.add_output(20.0, rsa_helper_1.public_key)
        tx0.finalize()

        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(7.0, rsa_helper_1.public_key)
        tx1.add_output(5.0, rsa_helper_2.public_key)
        tx1.add_output(3.0, rsa_helper_3.public_key)  # Total outputs = 15.0, fee = 5.0
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper_1.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()


        tx2 = Transaction()

        # Add the same UTXO two time
        tx2.add_input(tx1.get_hash(), 1)
        tx2.add_input(tx1.get_hash(), 1)

        tx2.add_output(6.0, rsa_helper_3.public_key)

        data_to_sign = tx2.get_data_to_sign(0)
        signature = rsa_helper_2.sign(data_to_sign)
        tx2.add_signature(signature, 0)
        tx2.finalize()

        tx3 = Transaction()
        tx3.add_input(tx1.get_hash(), 2)
        tx3.add_output(2.0, rsa_helper_1.public_key)
        data_to_sign = tx3.get_data_to_sign(0)
        signature = rsa_helper_3.sign(data_to_sign)
        tx3.add_signature(signature, 0)
        tx3.finalize()

        all_txs.append(tx1)
        all_txs.append(tx2)
        all_txs.append(tx3)

        handler = HandleTxs(pool)
        received_valid_txs = handler.handler(all_txs)
        expected_valid_txs = [tx1, tx3]


        expected_hashes = [tx.get_hash() for tx in expected_valid_txs]
        received_hashes = [tx.get_hash() for tx in received_valid_txs]

        self.assertEqual(len(expected_hashes), len(received_hashes), "List of transactions should be the same length.")
        self.assertEqual(expected_valid_txs, received_valid_txs, "Check valid transaction by hash.")

    # 12
    def test_tx_handler_valid_depend_tx(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()
        all_txs = []

        rsa_helper_1 = RSA.RSAHelper()
        rsa_helper_2 = RSA.RSAHelper()
        rsa_helper_3 = RSA.RSAHelper()

        tx0 = Transaction()
        tx0.add_output(20.0, rsa_helper_1.public_key)
        tx0.finalize()

        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(7.0, rsa_helper_1.public_key)
        tx1.add_output(5.0, rsa_helper_2.public_key)
        tx1.add_output(3.0, rsa_helper_3.public_key)  # Total outputs = 15.0, fee = 5.0
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper_1.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()


        tx2 = Transaction()
        tx2.add_input(tx1.get_hash(), 1)
        tx2.add_output(4.0, rsa_helper_3.public_key)
        data_to_sign = tx2.get_data_to_sign(0)
        signature = rsa_helper_2.sign(data_to_sign)
        tx2.add_signature(signature, 0)
        tx2.finalize()

        tx3 = Transaction()
        tx3.add_input(tx1.get_hash(), 2)
        tx3.add_input(tx2.get_hash(), 0)

        # Get the input from the tx1 (3.0) and tx2 (4.0)
        tx3.add_output(7, rsa_helper_1.public_key)

        data_to_sign_0 = tx3.get_data_to_sign(0)
        signature_0 = rsa_helper_3.sign(data_to_sign_0)
        tx3.add_signature(signature_0, 0)

        data_to_sign_1 = tx3.get_data_to_sign(1)
        signature_1 = rsa_helper_3.sign(data_to_sign_1)
        tx3.add_signature(signature_1, 1)

        tx3.finalize()


        all_txs.append(tx1)
        all_txs.append(tx2)
        all_txs.append(tx3)

        handler = HandleTxs(pool)
        received_valid_txs = handler.handler(all_txs)
        expected_valid_txs = [tx1, tx2, tx3]


        expected_hashes = [tx.get_hash() for tx in expected_valid_txs]
        received_hashes = [tx.get_hash() for tx in received_valid_txs]

        self.assertEqual(len(expected_hashes), len(received_hashes), "List of transactions should be the same length.")
        self.assertEqual(expected_valid_txs, received_valid_txs, "Check valid transaction by hash.")

    # 13
    def test_tx_handler_invalid_due_notexist_utxo(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()
        all_txs = []

        rsa_helper_1 = RSA.RSAHelper()
        rsa_helper_2 = RSA.RSAHelper()
        rsa_helper_3 = RSA.RSAHelper()

        tx0 = Transaction()
        tx0.add_output(20.0, rsa_helper_1.public_key)
        tx0.finalize()

        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(7.0, rsa_helper_1.public_key)
        tx1.add_output(5.0, rsa_helper_2.public_key)
        tx1.add_output(3.0, rsa_helper_3.public_key)  # Total outputs = 15.0, fee = 5.0
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper_1.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()


        tx2 = Transaction()

        # Add the not existing UTXO
        tx2.add_input(tx1.get_hash(), 4)

        tx2.add_output(6.0, rsa_helper_3.public_key)

        data_to_sign = tx2.get_data_to_sign(0)
        signature = rsa_helper_2.sign(data_to_sign)
        tx2.add_signature(signature, 0)
        tx2.finalize()

        tx3 = Transaction()
        tx3.add_input(tx1.get_hash(), 2)
        tx3.add_output(2.0, rsa_helper_1.public_key)
        data_to_sign = tx3.get_data_to_sign(0)
        signature = rsa_helper_3.sign(data_to_sign)
        tx3.add_signature(signature, 0)
        tx3.finalize()

        all_txs.append(tx1)
        all_txs.append(tx2)
        all_txs.append(tx3)

        handler = HandleTxs(pool)
        received_valid_txs = handler.handler(all_txs)
        expected_valid_txs = [tx1, tx3]


        expected_hashes = [tx.get_hash() for tx in expected_valid_txs]
        received_hashes = [tx.get_hash() for tx in received_valid_txs]

        self.assertEqual(len(expected_hashes), len(received_hashes), "List of transactions should be the same length.")
        self.assertEqual(expected_valid_txs, received_valid_txs, "Check valid transaction by hash.")

    # 14
    def test_tx_handler_valid_complex_tx(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()
        all_txs = []

        rsa_helper_1 = RSA.RSAHelper()
        rsa_helper_2 = RSA.RSAHelper()
        rsa_helper_3 = RSA.RSAHelper()
        rsa_helper_4 = RSA.RSAHelper()
        rsa_helper_5 = RSA.RSAHelper()

        tx0 = Transaction()
        tx0.add_output(25.0, rsa_helper_1.public_key)
        tx0.finalize()

        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        tx1 = Transaction()
        # Input from tx0/0 (25.0)
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(7.0, rsa_helper_1.public_key)
        tx1.add_output(6.0, rsa_helper_2.public_key)
        tx1.add_output(5.0, rsa_helper_3.public_key)
        tx1.add_output(2.0, rsa_helper_4.public_key)
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper_1.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()


        tx2 = Transaction()
        # Input from tx1/1 (6.0)
        tx2.add_input(tx1.get_hash(), 1)
        tx2.add_output(5.0, rsa_helper_3.public_key)
        data_to_sign = tx2.get_data_to_sign(0)
        signature = rsa_helper_2.sign(data_to_sign)
        tx2.add_signature(signature, 0)
        tx2.finalize()


        tx3 = Transaction()
        # Input from tx1/2 (6.0) AND tx2/0 (5.0)
        tx3.add_input(tx1.get_hash(), 2)
        tx3.add_input(tx2.get_hash(), 0)

        tx3.add_output(6, rsa_helper_4.public_key)
        tx3.add_output(4, rsa_helper_4.public_key)

        data_to_sign_0 = tx3.get_data_to_sign(0)
        signature_0 = rsa_helper_3.sign(data_to_sign_0)
        tx3.add_signature(signature_0, 0)

        data_to_sign_1 = tx3.get_data_to_sign(1)
        signature_1 = rsa_helper_3.sign(data_to_sign_1)
        tx3.add_signature(signature_1, 1)

        tx3.finalize()


        tx4 = Transaction()
        # Input from tx1/3 (2.0) AND tx3/0 (6.0) AND tx3/1 (4.0)
        tx4.add_input(tx1.get_hash(), 3)
        tx4.add_input(tx3.get_hash(), 0)
        tx4.add_input(tx3.get_hash(), 1)

        tx4.add_output(7, rsa_helper_5.public_key)
        tx4.add_output(5, rsa_helper_2.public_key)

        data_to_sign_0 = tx4.get_data_to_sign(0)
        signature_0 = rsa_helper_4.sign(data_to_sign_0)
        tx4.add_signature(signature_0, 0)

        data_to_sign_1 = tx4.get_data_to_sign(1)
        signature_1 = rsa_helper_4.sign(data_to_sign_1)
        tx4.add_signature(signature_1, 1)

        data_to_sign_2 = tx4.get_data_to_sign(2)
        signature_2 = rsa_helper_4.sign(data_to_sign_2)
        tx4.add_signature(signature_2, 2)

        tx4.finalize()



        all_txs.append(tx1)
        all_txs.append(tx2)
        all_txs.append(tx3)
        all_txs.append(tx4)

        handler = HandleTxs(pool)
        received_valid_txs = handler.handler(all_txs)
        expected_valid_txs = [tx1, tx2, tx3, tx4]


        expected_hashes = [tx.get_hash() for tx in expected_valid_txs]
        received_hashes = [tx.get_hash() for tx in received_valid_txs]

        self.assertEqual(len(expected_hashes), len(received_hashes), "List of transactions should be the same length.")
        self.assertEqual(expected_valid_txs, received_valid_txs, "Check valid transaction by hash.")

    # 15
    def test_tx_handler_valid_repeated_tx(self):
        pool = UTXOPool()
        all_txs = []

        rsa_helper_1 = RSA.RSAHelper()
        rsa_helper_2 = RSA.RSAHelper()


        tx0 = Transaction()
        tx0.add_output(25.0, rsa_helper_1.public_key)
        tx0.finalize()

        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        tx1 = Transaction()
        # Input from tx0/0 (25.0)
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(10.0, rsa_helper_2.public_key)
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper_1.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()


        tx2 = Transaction()
        # Input from tx1/0 (10.0)
        tx2.add_input(tx1.get_hash(), 0)
        tx2.add_output(10.0, rsa_helper_1.public_key)
        data_to_sign = tx2.get_data_to_sign(0)
        signature = rsa_helper_2.sign(data_to_sign)
        tx2.add_signature(signature, 0)
        tx2.finalize()


        tx3 = Transaction()
        # Input from tx2/0 (10.0)
        tx3.add_input(tx2.get_hash(), 0)
        tx3.add_output(10.0, rsa_helper_2.public_key)
        data_to_sign = tx3.get_data_to_sign(0)
        signature = rsa_helper_1.sign(data_to_sign)
        tx3.add_signature(signature, 0)
        tx3.finalize()


        all_txs.append(tx1)
        all_txs.append(tx2)
        all_txs.append(tx3)


        handler = HandleTxs(pool)
        received_valid_txs = handler.handler(all_txs)
        expected_valid_txs = [tx1, tx2, tx3]


        expected_hashes = [tx.get_hash() for tx in expected_valid_txs]
        received_hashes = [tx.get_hash() for tx in received_valid_txs]

        self.assertEqual(len(expected_hashes), len(received_hashes), "List of transactions should be the same length.")
        self.assertEqual(expected_valid_txs, received_valid_txs, "Check valid transaction by hash.")
        self.assertEqual(len(expected_hashes), len(received_hashes), "List of transactions should be the same length.")

    # 16
    def test_tx_handlerTXS_simple_valid_txs(self):
        pool = UTXOPool()
        all_txs = []

        rsa_helper_1 = RSA.RSAHelper()
        rsa_helper_2 = RSA.RSAHelper()
        rsa_helper_3 = RSA.RSAHelper()

        tx0 = Transaction()
        tx0.add_output(20.0, rsa_helper_1.public_key)
        tx0.finalize()

        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))


        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        # Input from tx0/0 (20.0/15.0/5.0)
        tx1.add_output(7.0, rsa_helper_1.public_key)
        tx1.add_output(5.0, rsa_helper_2.public_key)
        tx1.add_output(3.0, rsa_helper_3.public_key) # Total outputs = 15.0, fee = 5.0
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper_1.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()



        tx2 = Transaction()
        # Input from tx1/1 (5.0/5.0/0.0)
        tx2.add_input(tx1.get_hash(), 1)
        tx2.add_output(5.0, rsa_helper_3.public_key)

        data_to_sign = tx2.get_data_to_sign(0)
        signature = rsa_helper_2.sign(data_to_sign)
        tx2.add_signature(signature, 0)

        tx2.finalize()


        tx3 = Transaction()
        # Input from tx1/2 (3.0/2.0/1.0)
        tx3.add_input(tx1.get_hash(), 2)
        tx3.add_output(2.0, rsa_helper_1.public_key)

        data_to_sign = tx3.get_data_to_sign(0)
        signature = rsa_helper_3.sign(data_to_sign)
        tx3.add_signature(signature, 0)
        tx3.finalize()

        all_txs.append(tx1)
        all_txs.append(tx2)
        all_txs.append(tx3)

        handler = MaxFeeHandleTxs(pool)
        received_valid_txs = handler.handler(all_txs)
        expected_valid_txs = [tx1]


        expected_hashes = [tx.get_hash() for tx in expected_valid_txs]
        received_hashes = [tx.get_hash() for tx in received_valid_txs]

        self.assertEqual(len(expected_hashes), len(received_hashes), "List of transactions should be the same length.")
        self.assertEqual(expected_valid_txs, received_valid_txs, "Check valid transaction by hash.")

        for i in range(len(expected_hashes)):
            self.assertEqual(received_hashes[i], received_hashes[i], "List of transactions should be valid.")

    # 17
    def test_tx_handlerTXS_simple_valid_2_output(self):
        pool = UTXOPool()
        all_txs = []

        rsa_helper_1 = RSA.RSAHelper()
        rsa_helper_2 = RSA.RSAHelper()
        rsa_helper_3 = RSA.RSAHelper()

        tx0 = Transaction()
        tx0.add_output(17.0, rsa_helper_1.public_key)
        tx0.finalize()

        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))


        tx1 = Transaction()
        tx1.add_input(tx0.get_hash(), 0)
        # Input from tx0/0 (17.0/15.0/2.0)
        tx1.add_output(7.0, rsa_helper_1.public_key)
        tx1.add_output(5.0, rsa_helper_2.public_key)
        tx1.add_output(3.0, rsa_helper_3.public_key) # Total outputs = 15.0, fee = 5.0
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper_1.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()



        tx2 = Transaction()
        # Input from tx1/1 (5.0/5.0/0.0)
        tx2.add_input(tx1.get_hash(), 1)
        tx2.add_output(5.0, rsa_helper_3.public_key)

        data_to_sign = tx2.get_data_to_sign(0)
        signature = rsa_helper_2.sign(data_to_sign)
        tx2.add_signature(signature, 0)

        tx2.finalize()


        tx3 = Transaction()
        # Input from tx1/2 (3.0/1.0/2.0)
        tx3.add_input(tx1.get_hash(), 2)
        tx3.add_output(1.0, rsa_helper_1.public_key)

        data_to_sign = tx3.get_data_to_sign(0)
        signature = rsa_helper_3.sign(data_to_sign)
        tx3.add_signature(signature, 0)
        tx3.finalize()

        all_txs.append(tx1)
        all_txs.append(tx2)
        all_txs.append(tx3)

        handler = MaxFeeHandleTxs(pool)
        received_valid_txs = handler.handler(all_txs)
        expected_valid_txs = [tx1, tx3]


        expected_hashes = [tx.get_hash() for tx in expected_valid_txs]
        received_hashes = [tx.get_hash() for tx in received_valid_txs]

        self.assertEqual(len(expected_hashes), len(received_hashes), "List of transactions should be the same length.")
        self.assertEqual(expected_valid_txs, received_valid_txs, "Check valid transaction by hash.")

        for i in range(len(expected_hashes)):
            self.assertEqual(received_hashes[i], received_hashes[i], "List of transactions should be valid.")

    # 18
    def test_tx_handlerTXS_valid_invalid_complex_2(self):
        # 1. Create an empty UTXOPool.
        pool = UTXOPool()
        all_txs = []

        rsa_helper_1 = RSA.RSAHelper()
        rsa_helper_2 = RSA.RSAHelper()
        rsa_helper_3 = RSA.RSAHelper()
        rsa_helper_4 = RSA.RSAHelper()
        rsa_helper_5 = RSA.RSAHelper()

        tx0 = Transaction()
        tx0.add_output(20.0, rsa_helper_1.public_key)
        tx0.finalize()

        utxo0 = UTXO(tx0.get_hash(), 0)
        pool.add_utxo(utxo0, tx0.get_output(0))

        tx1 = Transaction()
        # Input from tx0/0 (20.0/20.0/0.0)
        tx1.add_input(tx0.get_hash(), 0)
        tx1.add_output(7.0, rsa_helper_1.public_key)
        tx1.add_output(6.0, rsa_helper_2.public_key)
        tx1.add_output(5.0, rsa_helper_3.public_key)
        tx1.add_output(2.0, rsa_helper_4.public_key)
        data_to_sign = tx1.get_data_to_sign(0)
        signature = rsa_helper_1.sign(data_to_sign)
        tx1.add_signature(signature, 0)
        tx1.finalize()


        tx2 = Transaction()
        # Input from tx1/1 (6.0/5.0/1.0)
        tx2.add_input(tx1.get_hash(), 1)
        tx2.add_output(5.0, rsa_helper_3.public_key)
        data_to_sign = tx2.get_data_to_sign(0)
        signature = rsa_helper_2.sign(data_to_sign)
        tx2.add_signature(signature, 0)
        tx2.finalize()


        tx3 = Transaction()
        # Input from tx1/2 (5.0) AND tx2/0 (5.0) (10.0/9.0/1.0)
        tx3.add_input(tx1.get_hash(), 2)
        tx3.add_input(tx2.get_hash(), 0)

        tx3.add_output(5, rsa_helper_4.public_key)
        tx3.add_output(4, rsa_helper_4.public_key)

        data_to_sign_0 = tx3.get_data_to_sign(0)
        signature_0 = rsa_helper_3.sign(data_to_sign_0)
        tx3.add_signature(signature_0, 0)

        data_to_sign_1 = tx3.get_data_to_sign(1)
        signature_1 = rsa_helper_3.sign(data_to_sign_1)
        tx3.add_signature(signature_1, 1)

        tx3.finalize()


        tx4 = Transaction()
        # Input from tx1/3 (2.0) AND tx3/0 (6.0) AND tx3/1 (4.0)
        tx4.add_input(tx1.get_hash(), 3)
        tx4.add_input(tx3.get_hash(), 0)
        # incorrect index
        tx4.add_input(tx3.get_hash(), 4)

        tx4.add_output(7, rsa_helper_5.public_key)
        tx4.add_output(5, rsa_helper_2.public_key)

        # incorrect addr to verify
        data_to_sign_0 = tx4.get_data_to_sign(0)
        signature_0 = rsa_helper_3.sign(data_to_sign_0)
        tx4.add_signature(signature_0, 0)

        # incorrect signature
        data_to_sign_1 = tx4.get_data_to_sign(1)
        signature_1 = rsa_helper_4.sign(data_to_sign_1)
        signature_1_invalid = bytearray(signature_1)
        signature_1_invalid[-1] ^= 0x01
        signature_1_invalid = bytes(signature_1_invalid)
        tx4.add_signature(signature_1_invalid, 1)

        tx4.finalize()


        all_txs.append(tx1)
        all_txs.append(tx2)
        all_txs.append(tx3)
        all_txs.append(tx4)

        handler = MaxFeeHandleTxs(pool)
        received_valid_txs = handler.handler(all_txs)
        expected_valid_txs = [tx2, tx3] #tx2=tx3=0.1

        expected_hashes = [tx.get_hash() for tx in expected_valid_txs]
        received_hashes = [tx.get_hash() for tx in received_valid_txs]

        self.assertEqual(len(expected_hashes), len(received_hashes), "List of transactions should be the same length.")
        self.assertEqual(expected_valid_txs, received_valid_txs, "Check valid transaction by hash.")
        self.assertEqual(len(expected_hashes), len(received_hashes), "List of transactions should be the same length.")


if __name__ == '__main__':
    unittest.main()