class UTXOPool:

    def __init__(self, uPool = None):
        """Vytvorí nový prázdny UTXOPool"""
        if uPool == None:
            self.H = {}
        else:
            """Vytvorí nový UTXOPool, ktorý je kópiou uPool"""
            self.H = uPool.H.copy()


    def add_utxo(self, utxo, tx_out):
        """Pridá namapovanie z UTXO utxo do transackčného výstupu txOut v poole"""
        self.H[utxo] = tx_out

    def remove_utxo(self, utxo):
        """Odstráni UTXO utxo z poolu"""
        if utxo in self.H:
            del self.H[utxo]

    def get_tx_output(self, utxo):
        """
        @return: výstup transakcie zodpovedajúci UTXO utxo alebo None, ak
                 utxo nie je v poole.
        """
        return self.H.get(utxo, None)

    def contains(self, utxo):
        """@return: True ak UTXO utxo je v poole a inak False"""
        return utxo in self.H

    def get_all_utxo(self):
        """Vráti list všetkých UTXOs v poole"""
        return list(self.H.keys())
