import UTXOPool
import UTXO
from RSA import RSAHelper

# Artem Delikatnyi
class HandleTxs:
    def __init__(self, utxo_pool):
         # IMPLEMENTOVAŤ
        """
        Vytvorí verejný ledger (účtovnú knihu), ktorého aktuálny UTXOPool
        (zbierka nevyčerpaných transakčných výstupov) je utxo_pool. Malo by to vytvoriť bezpečnú kópiu
        utxo_pool pomocou konštruktora UTXOPool (UTXOPool uPool).
        """
        self.utxo_pool = UTXOPool.UTXOPool(utxo_pool)

    def UTXOPoolGet(self):
        # IMPLEMENTOVAŤ
        """
        @return aktuálny UTXO pool.
        Ak nenájde žiadny aktuálny UTXO pool, tak vráti prázdny (nie nulový) objekt UTXOPool.
        """
        if self.utxo_pool:
            return self.utxo_pool
        return UTXOPool.UTXOPool()

    @staticmethod
    def txIsValid(tx, utxo_pool, tx_pool_utxo):
        # IMPLEMENTOVAŤ
        """
        @return true, ak
        ? (1) sú všetky nárokované výstupy tx v aktuálnom UTXO pool,
        ? (2) podpisy na každom vstupe tx sú platné,
        + (3) žiadne UTXO nie je nárokované viackrát,
        + (4) všetky výstupné hodnoty tx sú nezáporné a
        + (5) súčet vstupných hodnôt txs je väčší alebo rovný súčtu jej
        výstupných hodnôt; a false inak.
        """

        inp_val = 0
        op_val = 0
        used_utxos = []
        index = 0

        if tx.is_coinbase():
            op = tx.get_outputs()
            if len(op) != 1:
                return False
            if op[0].value < 0:
                return False
            return True


        for inpt in tx.get_inputs():
            utxo = UTXO.UTXO(inpt.prevTxHash, inpt.outputIndex)

            tx_output = utxo_pool.get_tx_output(utxo)
            if not utxo_pool.contains(utxo):
                return False

            if tx_pool_utxo is not None and utxo in tx_pool_utxo:
                return False

            message = tx.get_data_to_sign(index)
            index+=1

            if tx_output.is_multisig:
                print("It is multisig Tx")
                signatures = inpt.signatures
                multisig_keys = tx_output.multisig_keys
                required = tx_output.required
                if not RSAHelper.verify_multisig(multisig_keys, message, signatures, required):
                    print("INVALID multisig Tx")
                    return False
                else:
                    print("CORRECT multisig Tx")

            else:
                if not inpt.signatures:
                    return False
                signature = inpt.signatures[0]
                addr = tx_output.address


                if signature is None or not RSAHelper.verify(addr, message, signature):
                    return False

            if utxo in used_utxos:
                return False
            else:
                used_utxos.append(utxo)
            if tx_output:
                inp_val += tx_output.value

        for op in tx.get_outputs():
            if op.value < 0:
                return False
            op_val += op.value

        print("OP:", op_val)
        print("INP:", inp_val)

        if inp_val < op_val:
            return False


        return True

    def handler(self, possible_txs, tx_pool_utxo=None):
        # IMPLEMENTOVAŤ
        """
        Spracováva každú epochu (iteráciu) prijímaním neusporiadaného radu navrhovaných
        transakcií, kontroluje správnosť každej transakcie, vracia pole vzájomne
        platných prijatých transakcií a aktualizuje aktuálny UTXO pool podľa potreby.
        """

        valid_txs = []
        invalid_txs = []

        for tx in possible_txs:
            if HandleTxs.txIsValid(tx, utxo_pool=self.utxo_pool, tx_pool_utxo=tx_pool_utxo):
                if tx.is_coinbase():
                    utxo0 = UTXO.UTXO(tx.get_hash(), 0)
                    self.utxo_pool.add_utxo(utxo0, tx.get_output(0))
                    valid_txs.append(tx)
                    return valid_txs
                valid_txs.append(tx)
                index = 0

                for inp in tx.get_inputs():
                    used_utxo = UTXO.UTXO(inp.prevTxHash, inp.outputIndex)

                    if tx_pool_utxo is not None and used_utxo in tx_pool_utxo:
                        tx_pool_utxo.remove(used_utxo)

                    if self.utxo_pool.contains(used_utxo):
                        self.utxo_pool.remove_utxo(used_utxo)

                for op in tx.get_outputs():
                    hash_tx = tx.get_hash()
                    new_utxo = UTXO.UTXO(hash_tx, index)
                    if not self.utxo_pool.contains(new_utxo):
                        self.utxo_pool.add_utxo(new_utxo, op)
                    index += 1
            else:
                for inp in tx.get_inputs():
                    used_utxo = UTXO.UTXO(inp.prevTxHash, inp.outputIndex)
                    if tx_pool_utxo is not None and used_utxo in tx_pool_utxo:
                        tx_pool_utxo.remove(used_utxo)
                invalid_txs.append(tx)
                return valid_txs, invalid_txs

        return valid_txs, invalid_txs
