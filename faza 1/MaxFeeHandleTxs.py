import UTXOPool
import UTXO
from rsa.RSA import RSAHelper

# Artem Delikatnyi
class MaxFeeHandleTxs:
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


    def txIsValid(self, tx):
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

        for inpt in tx.get_inputs():
            utxo = UTXO.UTXO(inpt.prevTxHash, inpt.outputIndex)
            tx_output = self.utxo_pool.get_tx_output(utxo)
            if not self.utxo_pool.contains(utxo):
                return False
            message = tx.get_data_to_sign(index)
            index+=1
            addr = tx_output.address
            signature = inpt.signature

            if inpt.signature is None or not RSAHelper.verify(addr, message, signature):
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

        if inp_val < op_val:
            return False

        return True

    def handler(self, possible_txs):
        # IMPLEMENTOVAŤ
        """
        Spracováva každú epochu (iteráciu) prijímaním neusporiadaného radu navrhovaných
        transakcií, kontroluje správnosť každej transakcie, vracia pole vzájomne
        platných prijatých transakcií a aktualizuje aktuálny UTXO pool podľa potreby.
        """

        valid_txs = {}

        for tx in possible_txs:
            if self.txIsValid(tx):
                inp_val = 0
                op_val = 0
                index = 0

                for inpt in tx.get_inputs():
                    used_utxo = UTXO.UTXO(inpt.prevTxHash, inpt.outputIndex)

                    tx_output = self.utxo_pool.get_tx_output(used_utxo)
                    if tx_output:
                        inp_val += tx_output.value

                    if self.utxo_pool.contains(used_utxo):
                        self.utxo_pool.remove_utxo(used_utxo)

                for op in tx.get_outputs():
                    op_val += op.value

                    hash_tx = tx.get_hash()
                    new_utxo = UTXO.UTXO(hash_tx, index)
                    index+=1
                    if not self.utxo_pool.contains(new_utxo):
                        self.utxo_pool.add_utxo(new_utxo, op)

                fee = inp_val - op_val
                valid_txs[tx] = fee

        sorted_txs = sorted(valid_txs.items(), key=lambda item: item[1], reverse=True)
        max_fee_transactions = [tx for tx, fee in sorted_txs if fee == sorted_txs[0][1]]

        return max_fee_transactions
