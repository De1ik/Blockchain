import hashlib
import struct
from RSA import RSAHelper

class Transaction:

    class Input:
        def __init__(self, prev_hash, index):
            self.prevTxHash =  prev_hash[:] if prev_hash else None
            self.outputIndex = index
            self.signatures = []

        def add_signature(self, sig):
            self.signatures.append(sig)


        def __eq__(self, other):
            if not isinstance(other, Transaction.Input):
                return False
            return (self.prevTxHash == other.prevTxHash and
                    self.outputIndex == other.outputIndex and
                    self.signatures == other.signatures)


        def __hash__(self):
            return hash((bytes(self.prevTxHash) if self.prevTxHash else b'',
                         self.outputIndex,
                         bytes(self.signatures) if self.signatures else b''))


    class Output:
        def __init__(self, value, addr, multisig_keys, required):
            self.value = value
            self.is_multisig = False if multisig_keys is None else multisig_keys
            self.multisig_keys = multisig_keys
            self.required = required

            if self.multisig_keys is not None and addr is None:
                # self.address = self.serialize_key(self.create_multisig_addr())
                self.address = self.create_multisig_addr()
            # elif addr is not None:
            #     print("SER")
            #     self.address = self.serialize_key(addr)
            else:
                self.address = addr

        def create_multisig_addr(self):
            rsa_helper_multisig_pvk = RSAHelper()
            return rsa_helper_multisig_pvk.public_key

        def get_multisig_addr(self):
            return self.address

        def serialize_key(self, address):
            pem = RSAHelper.serialize_pb_key(address)
            return pem

        def deserialize_key(self, address):
            key = RSAHelper.deserialize_pb_key(address)
            return key


        def __eq__(self, other):
            if not isinstance(other, Transaction.Output):
                return False
            return (self.value == other.value and
                    # self.deserialize_key(self.address).e == self.deserialize_key(other.address).e and
                    # self.deserialize_key(self.address).n == self.deserialize_key(other.address).n)

                    self.address.e == other.address.e and
                    self.address.n == other.address.n)

        def __hash__(self):
            # return hash((round(self.value * 10000), self.deserialize_key(self.address).e, self.deserialize_key(self.address).n))
            return hash((round(self.value * 10000), self.address.e, self.address.n))



    def __init__(self, tx=None, coin=None, address=None):
        if tx is not None:
            self.hash = tx.hash[:] if tx.hash is not None else None
            self.inputs = tx.inputs.copy()
            self.outputs = tx.outputs.copy()
            self.coinbase = False
        elif coin is not None and address is not None:
            print("Coinbase transaction created")
            self.coinbase = True
            self.inputs = []
            self.outputs = []
            self.add_output(coin, address)
            self.finalize()
        elif tx is None:
            print("Basic transaction created")
            self.inputs = []
            self.outputs = []
            self.coinbase = False
            self.hash = None

    def is_coinbase(self):
        return self.coinbase

    def add_input(self, prev_tx_hash, output_index):
        inpt = self.Input(prev_tx_hash, output_index)
        self.inputs.append(inpt)

    def add_output(self, value, address = None, multisig_keys = None, required = 1):
        op = self.Output(value, address, multisig_keys, required)
        self.outputs.append(op)

    def remove_input(self, index):
        del self.inputs[index]

    def remove_input_utxo(self, utxo):
        for i, inpt in enumerate(self.inputs):
            if inpt.prevTxHash == utxo.prevTxHash and inpt.outputIndex == utxo.outputIndex:
                del self.inputs[i]
                return

    def get_data_to_sign(self, index):
        sig_data = []
        if index >= len(self.inputs):
            return None
        inpt = self.inputs[index]
        prev_tx_hash = inpt.prevTxHash
        output_index = struct.pack('>I', inpt.outputIndex)

        if prev_tx_hash:
            sig_data.extend(prev_tx_hash)
        sig_data.extend(output_index)

        for op in self.outputs:
            value_bytes = struct.pack('>d', op.value)  # big-endian double

            # public_numbers = RSAHelper.deserialize_pb_key(op.address).public_numbers()
            public_numbers = op.address.public_numbers()
            address_exponent = public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, byteorder='big')
            address_modulus = public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, byteorder='big')

            sig_data.extend(value_bytes)
            sig_data.extend(address_exponent)
            sig_data.extend(address_modulus)

        return bytes(sig_data)

    def add_signature(self, signature, index):
        self.inputs[index].add_signature(signature)

    def get_tx(self):
        tx = []
        for inpt in self.inputs:
            prev_tx_hash = inpt.prevTxHash
            output_index = struct.pack('>I', inpt.outputIndex)
            signatures = inpt.signatures

            if prev_tx_hash:
                tx.extend(prev_tx_hash)
            tx.extend(output_index)

            if signatures:
                for sig in signatures:
                    tx.extend(sig)

        for op in self.outputs:
            value_bytes = struct.pack('>d', op.value)  # big-endian double

            # public_numbers = RSAHelper.deserialize_pb_key(op.address).public_numbers()
            public_numbers = op.address.public_numbers()
            address_exponent = public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, byteorder='big')
            address_modulus = public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, byteorder='big')

            tx.extend(value_bytes)
            tx.extend(address_exponent)
            tx.extend(address_modulus)

        return bytes(tx)

    def finalize(self):
        try:
            md = hashlib.sha256()
            md.update(self.get_tx())
            self.hash = md.digest()
        except Exception as e:
            print(e)

    def set_hash(self, h):
        self.hash = h

    def get_hash(self):
        return self.hash

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs

    def get_input(self, index):
        if index < len(self.inputs):
            return self.inputs[index]
        return None

    def get_output(self, index):
        if index < len(self.outputs):
            return self.outputs[index]
        return None

    def num_inputs(self):
        return len(self.inputs)

    def num_outputs(self):
        return len(self.outputs)

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return (self.inputs == other.inputs and
                self.outputs == other.outputs and
                self.hash == other.hash)

    def __hash__(self):
        hash_code = 1
        for i in range(self.num_inputs()):
            hash_code = hash_code * 31 + hash(self.inputs[i])

        for i in range(self.num_outputs()):
            hash_code = hash_code * 31 + hash(self.outputs[i])

        return hash_code