import random
from Transaction import Transaction
from ByzantineNode import ByzantineNode
from TrustedNode import TrustedNode


def main(p_graph, p_byzantine, p_txDistribution, numRounds):
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

                    # j follower i
                    if not followees[j][i]:
                        continue

                    allProposals.setdefault(j, []).append([tx.id, i])

        for i in range(numNodes):
            if i in allProposals:
                nodes[i].followeesReceive(allProposals[i])

    for i, node in enumerate(nodes):
        transactions = node.followersSend()
        print(f"Transaction ids that Node {i} believes consensus on:")
        for tx in transactions:
            print(tx.id)
        print("\n")


if __name__ == "__main__":
    main(0.1, 0.45, 0.01, 20)
