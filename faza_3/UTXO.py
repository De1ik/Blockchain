class UTXO:

    def __init__(self, tx_hash, index):
        """
        Vytvorí nové UTXO zodpovedajúce výstupu s indexom <index> v transakcii,
        ktorej hash je tx_hash
        """
        # Hash transakcie, z ktorej toto UTXO pochádza
        self.txHash = tx_hash[:] if tx_hash else None
        # Index prislúchajúceho výstupu v transakcii
        self.index = index

    def get_tx_hash(self):
        """@return: transakčný hash tohto UTXO"""
        return self.txHash

    def get_index(self):
        """@return: index tohto UTXO"""
        return self.index

    def __eq__(self, other):
        """
        Porovná toto UTXO s tým, ktoré bolo zadané v other, považuje ich za
        rovnocenné ak majú pole txHash s rovnakým obsahom a rovnaké hodnoty
        index
        """
        if not isinstance(other, UTXO):
            return False
        if (self.txHash is not None and len(self.txHash) != len(other.txHash)) or (self.index != other.index):
            return False
        return self.txHash == other.txHash

    def __hash__(self):
        """
            * Jednoduchá implementácia UTXO hashCode, ktorá rešpektuje rovnosť UTXOs //
            * (t.j. utxo1.equals (utxo2) => utxo1.hashCode () == utxo2.hashCode ())
        :return:
        """
        hash_code = 1
        hash_code = hash_code * 17 + self.index
        hash_code = hash_code * 31 + hash(self.txHash)
        return hash_code

    def __lt__(self, other):
        """
        Porovná toto UTXO so špecifikovaným v utxo
        """
        if self.index < other.index:
            return True
        elif self.index > other.index:
            return False
        else:
            return self.txHash < other.txHash

    def __gt__(self, other):
        """
        Porovná toto UTXO so špecifikovaným v utxo
        """
        if self.index > other.index:
            return True
        elif self.index < other.index:
            return False
        else:
            return self.txHash > other.txHash
