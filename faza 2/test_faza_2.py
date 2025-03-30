import unittest
import itertools
import time
import random

from Transaction import Transaction
from ByzantineNode import ByzantineNode
from TrustedNode import TrustedNode

# the same code as in simulation.py but we do not print result, but save it
def main_return_consensus(p_graph, p_byzantine, p_txDistribution, numRounds):
    numNodes = 100
    nodes = []
    for _ in range(numNodes):
        if random.random() < p_byzantine:
            nodes.append(ByzantineNode(p_graph, p_byzantine, p_txDistribution, numRounds))
        else:
            nodes.append(TrustedNode(p_graph, p_byzantine, p_txDistribution, numRounds))

    followees = [[False for _ in range(numNodes)] for _ in range(numNodes)]
    for i in range(numNodes):
        for j in range(numNodes):
            if i != j and random.random() < p_graph:
                followees[i][j] = True

    for i in range(numNodes):
        nodes[i].followeesSet(followees[i])

    numTx = 500
    validTxIds = {random.randint(0, 10**9) for _ in range(numTx)}

    for i in range(numNodes):
        pending = set()
        for txID in validTxIds:
            if random.random() < p_txDistribution:
                pending.add(Transaction(txID))
        nodes[i].pendingTransactionSet(pending)

    for _ in range(numRounds):
        allProposals = {}
        for i, node in enumerate(nodes):
            proposals = node.followersSend()
            for tx in proposals:
                if tx.id not in validTxIds:
                    continue
                for j in range(numNodes):
                    if not followees[j][i]:
                        continue
                    allProposals.setdefault(j, []).append([tx.id, i])

        for i in range(numNodes):
            if i in allProposals:
                nodes[i].followeesReceive(allProposals[i])

    results = []
    for node in nodes:
        tx_ids = {tx.id for tx in node.followersSend()}
        is_trusted = isinstance(node, TrustedNode)
        results.append((is_trusted, tx_ids))
    return results


class TestConsensusSnowball(unittest.TestCase):

    def run_consensus_test(self, p_graph, p_byzantine, p_txDistribution, numRounds):
        start = time.time()
        results = main_return_consensus(p_graph, p_byzantine, p_txDistribution, numRounds)
        duration = time.time() - start

        trusted_sets = [frozenset(r) for is_trusted, r in results if is_trusted]

        consensus = len(set(trusted_sets)) == 1
        if consensus:
            consensus_set = trusted_sets[0]
            print(f"\n✅ Consensus REACHED | The number of txs: {len(consensus_set)} | Duration: {duration:.2f} s")
        else:
            print(f"\n❌ Consensus NOT reached | Different versions among TrustedNode | Duration: {duration:.2f} s")
            for idx, tx_set in enumerate(trusted_sets):
                print(f"  Node {idx}: {sorted(tx_set)}")

        self.assertTrue(consensus, f"No consensus for the parameters: graph={p_graph}, byzantine={p_byzantine}, txDistrib={p_txDistribution}, rounds={numRounds}")

    def test_all_parameter_combinations(self):
        p_graph_values = [0.1, 0.2, 0.3]
        p_byzantine_values = [0.15, 0.30, 0.45]
        p_txDistribution_values = [0.01, 0.05, 0.10]
        numRounds_values = [10, 20]

        for combo in itertools.product(p_graph_values, p_byzantine_values, p_txDistribution_values, numRounds_values):
            # allow to run the same test ,many times, even when some of the is error
            with self.subTest(combo=combo):
                print(f"\n--- Input parameters: p_graph={combo[0]}, p_byzantine={combo[1]}, p_txDistrib={combo[2]}, numRounds={combo[3]} ---")
                self.run_consensus_test(*combo)


if __name__ == '__main__':
    unittest.main()
