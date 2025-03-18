import hashlib
import struct

class Transaction:

    class Input:
        def __init__(self, prev_hash, index):
            # hash transakcie, ktorej výstup sa ide použiť
            self.prevTxHash =  prev_hash[:] if prev_hash else None
            # použitý index výstupu v predchádzajúcej transakcii
            self.outputIndex = index
            # podpis vytvorený na kontrolu platnosti
            self.signature = None
            # self.prevPublicAddress = prevPublicAddress

        def add_signature(self, sig):
            self.signature = sig[:] if sig else None

    class Output:
        def __init__(self, value, addr):
            # hodnota výstupu v bitcoinoch
            self.value = value
            # adresa alebo verejný kľúč prijímateľa
            self.address = addr

    def __init__(self, tx=None):
        if tx is None:
            self.inputs = []
            self.outputs = []
            # hash transakcie, jej unikátne id
            self.hash = None
        else:
            # hash transakcie, jej unikátne id
            self.hash = tx.hash[:] if tx.hash is not None else None
            self.inputs = tx.inputs.copy()
            self.outputs = tx.outputs.copy()


    def add_input(self, prev_tx_hash, output_index):
        inpt = self.Input(prev_tx_hash, output_index)
        self.inputs.append(inpt)

    def add_output(self, value, address):
        op = self.Output(value, address)
        self.outputs.append(op)

    def remove_input(self, index):
        del self.inputs[index]

    def remove_input_utxo(self, utxo):
        for i, inpt in enumerate(self.inputs):
            if inpt.prevTxHash == utxo.prevTxHash and inpt.outputIndex == utxo.outputIndex:
                del self.inputs[i]
                return

    def get_data_to_sign(self, index):
        # i-ty vstup a všetky výstupy
        sig_data = []
        if index >= len(self.inputs):
            return None
        inpt = self.inputs[index]
        # print('Hash T:', inpt.prevTxHash)
        # print('Output Index T:', inpt.outputIndex)
        # print('SIGN T:', inpt.signature)
        prev_tx_hash = inpt.prevTxHash
        output_index = struct.pack('>I', inpt.outputIndex)

        if prev_tx_hash:
            sig_data.extend(prev_tx_hash)
        sig_data.extend(output_index)

        for op in self.outputs:
            value_bytes = struct.pack('>d', op.value)  # big-endian double

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
            signature = inpt.signature

            if prev_tx_hash:
                tx.extend(prev_tx_hash)
            tx.extend(output_index)

            if signature:
                tx.extend(signature)

        # for op in self.outputs:
        #     value = struct.pack('>d', op.value)
        #     # fix 100-101 / 145-146
        #     address_exponent = op.address.get_exponent().to_bytes((op.address.get_exponent().bit_length() + 7) // 8, 'big')
        #     address_modulus = op.address.get_modulus().to_bytes((op.address.get_modulus().bit_length() + 7) // 8, 'big')
        #
        #     tx.extend(value)
        #     tx.extend(address_exponent)
        #     tx.extend(address_modulus)

        for op in self.outputs:
            # Конвертируем значение (double) в байты
            value_bytes = struct.pack('>d', op.value)  # big-endian double

            # Получаем экспоненту и модуль из публичного ключа
            public_numbers = op.address.public_numbers()
            address_exponent = public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, byteorder='big')
            address_modulus = public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, byteorder='big')

            # Добавляем все байты в sig_data
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
