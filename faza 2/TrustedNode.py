from Node import Node
from Transaction import Transaction

# Artem Delikatnyi
class TrustedNode(Node):
    def __init__(self, p_graph, p_byzantine, p_txDistribution, numRounds):
        self.followees = set()
        self.p_byzantine = p_byzantine
        self.p_graph = p_graph
        self.p_txDistribution = p_txDistribution

        # self.k = 2
        self.beta = 3 if numRounds >= 20 else 2
        self.beta = self.beta + int(self.p_byzantine * 10) + (2 if self.p_txDistribution > 0.5 else 0)
        # self.beta = self.beta + int(self.p_byzantine * 10)
        self.tx_confidence = {}  # tx_id -> consecutive wins
        self.accepted = set()
        self.pending = set()
        self.round = 0
        self.observed = set()

    def followeesSet(self, followees):
        self.followees = {i for i, val in enumerate(followees) if val}

    def pendingTransactionSet(self, pendingTransactions):
        for tx in pendingTransactions:
            self.tx_confidence[tx.id] = 0
            self.pending.add(tx)
            self.observed.add(tx.id)

    def followersSend(self):
        self.round += 1
        return self.pending | {Transaction(tx_id) for tx_id in self.accepted}

    def followeesReceive(self, candidates):
        vote_counts = {}

        for tx_id, sender_id in candidates:
            if sender_id not in self.followees:
                continue
            vote_counts[tx_id] = vote_counts.get(tx_id, 0) + 1
            self.observed.add(tx_id)

        honest_followees = int((1 - self.p_byzantine) * len(self.followees))
        support_fraction = 0.6 if self.p_graph > 0.5 else 0.4
        required_support = max(2, int(honest_followees * support_fraction))
        # required_support = max(2, int(honest_followees * 0.5))
        # required_support = max(2, int(len(self.followees) * 0.4))

        for tx_id, count in vote_counts.items():
            if count >= required_support:
                self.tx_confidence[tx_id] = self.tx_confidence.get(tx_id, 0) + 1
            else:
                self.tx_confidence[tx_id] = 0

            if self.tx_confidence[tx_id] >= self.beta:
                self.accepted.add(tx_id)
                self.pending.discard(Transaction(tx_id))

        for tx_id in vote_counts:
            if tx_id not in self.accepted:
                self.pending.add(Transaction(tx_id))


