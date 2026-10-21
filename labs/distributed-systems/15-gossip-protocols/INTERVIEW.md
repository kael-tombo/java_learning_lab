# Gossip Protocols - Interview Preparation

> Key interview questions about gossip-based communication protocols.

---

## Core Interview Questions

### Q1: How does the gossip protocol work?
**Answer**: Each node periodically picks a random peer and exchanges state. Information spreads exponentially: O(log N) rounds for all nodes to receive an update. Each round doubles the informed nodes. The fanout (number of peers per round) controls propagation speed vs bandwidth.

### Q2: Compare push-based vs pull-based gossip
**Answer**: Push: infected node randomly selects peer and sends state. Faster initial spread. Pull: uninfected node asks random peer for updates. Better for high infection rates. Hybrid: push on update, pull periodically. Cassandra uses push-pull gossip.

### Q3: How does DynamoDB use gossip for membership?
**Answer**: Each DynamoDB node maintains a complete membership list. Gossip round: node picks random peer, exchanges membership state. Includes suspected status (based on failure detector). Nodes propagate observed failures. Eventual convergence of membership view.

### Q4: What is the "infection rate" in gossip protocols?
**Answer**: Percentage of nodes that have received an update. In ideal gossip (fanout = 1): round 0: 1 node infected. Round 1: 2 nodes. Round 2: 4 nodes. Round N: 2^N nodes. For 1000 nodes, need log2(1000) ~ 10 rounds. Each round ~ 100ms => converge in 1 second.

### Q5: What are Merkle trees used for in anti-entropy?
**Answer**: Merkle trees enable efficient comparison of data across replicas. Each leaf = hash of data block. Parent = hash of children. Compare root hashes; if different, recurse down tree to find differing leaves. Used in DynamoDB, Cassandra for anti-entropy repair.

## Company-Specific Focus

| Company | Gossip Focus |
|---------|-------------|
| Amazon | "DynamoDB gossip-based membership" |
| Apache | "Cassandra / Akka gossip protocols" |
| Hashicorp | "Serf/memberlist gossip + SWIM" |
| Microsoft | "Azure Service Fabric gossip" |

## LeetCode Connections

| Problem | # | Gossip Concept |
|---------|---|---------------|
| Rotting Oranges | 994 | Multi-source propagation |
| Network Delay Time | 743 | Gossip propagation time |
| Walls and Gates | 286 | BFS propagation = gossip |
| Time Needed to Inform All | 1376 | Hierarchical gossip |
| Clone Graph | 133 | Graph gossip replication |

## System Design Connections

- **Design a Cluster Membership Service**: Gossip for node discovery
- **Design a Distributed Database**: Gossip for metadata sync
- **Design a Service Registry**: Gossip for service discovery
- **Design a Config Distribution**: Gossip for config propagation

> **Key Insight**: Gossip protocols are used in many production systems for membership, failure detection, and metadata dissemination. Know the convergence math.