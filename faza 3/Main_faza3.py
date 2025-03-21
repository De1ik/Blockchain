import hashlib
from RSA import RSAHelper
from Block import Block
from Blockchain import Blockchain
from HandleBlocks import HandleBlocks
from Transaction import Transaction


class MainFaza3:
    @staticmethod
    def main():

        bob = RSAHelper()
        alice = RSAHelper()
        cyril = RSAHelper()

        genesis_block = Block(None, bob.public_key())
        genesis_block.finalize()
        blockchain = Blockchain(genesis_block)
        handle_blocks = HandleBlocks(blockchain)

        block1 = Block(genesis_block.get_hash(), alice.public_key)
        # block1 = HandleBlocks.block_create(alice.public_key)
        tx1 = MainFaza3.Tx()
        tx1.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx1.add_output(1, alice.public_key)
        tx1.add_output(1, alice.public_key)
        tx1.add_output(1.125, alice.public_key)
        tx1.sign_tx(bob.private_key, 0)
        block1.transaction_add(tx1)
        block1.finalize()
        print("Block1 Valid check:", handle_blocks.block_process(block1))

        block2 = Block(genesis_block.get_hash(), bob.public_key)
        tx2 = MainFaza3.Tx()
        tx2.add_input(genesis_block.get_coinbase().get_hash(), 0)
        tx2.add_output(1, bob.public_key)
        tx2.add_output(1, bob.public_key)
        tx2.add_output(1.125, bob.public_key)
        tx2.sign_tx(bob.private_key, 0)
        block2.transaction_add(tx2)
        block2.finalize()
        print("Block2 Valid check:", handle_blocks.block_process(block2))

        block3 = Block(block1.get_hash(), bob.public_key)
        tx3 = MainFaza3.Tx()
        tx3.add_input(tx1.get_hash(), 0)
        tx3.add_input(tx1.get_hash(), 1)
        tx3.add_output(2, cyril.public_key)
        tx3.sign_tx(alice.private_key, 0)
        tx3.sign_tx(alice.private_key, 1)
        block3.transaction_add(tx3)
        block3.finalize()
        print("Block3 Valid check:", handle_blocks.block_process(block3))

        block4 = Block(block3.get_hash(), bob.public_key)
        tx4 = MainFaza3.Tx()
        tx4.add_input(tx3.get_hash(), 0)
        tx4.add_output(1.5, bob.public_key)
        tx4.add_output(0.5, bob.public_key)
        tx4.sign_tx(cyril.private_key, 0)
        block4.transaction_add(tx4)
        block4.finalize()
        print("Block4 Valid check:", handle_blocks.block_process(block4))

    class Tx(Transaction):
        def sign_tx(self, sk, input):
            try:
                sig = sk.sign(self.get_data_to_sign(input))
                self.add_signature(sig, input)
                self.finalize()
            except Exception as e:
                raise RuntimeError(e)

    class MultiSigTx(Transaction):
        def sign_tx(self, sk, input):
            try:
                sig = sk.sign(self.get_data_to_sign(input))
                self.add_signature(sig, input)
                self.finalize()
            except Exception as e:
                raise RuntimeError(e)


if __name__ == "__main__":
    MainFaza3.main()
