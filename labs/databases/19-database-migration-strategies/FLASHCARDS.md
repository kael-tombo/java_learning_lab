# Flashcards: Database Migration Strategies

## Q: What is database migration strategies?
**A:** Strategy that distributes data across multiple independent database instances for scalability.

## Q: What is a routing key?
**A:** Column(s) determining which node stores each row of data.

## Q: Range vs Hash distribution?
**A:** Range: value ranges, good for ordered queries, hotspot risk. Hash: hash function, even distribution, breaks range locality.

## Q: How does consistent hashing work?
**A:** Keys and nodes on a hash ring. Keys assigned to nearest node clockwise. Node changes move only K/N keys.

## Q: What are virtual nodes (vnodes)?
**A:** Each physical node represented by multiple ring positions for better distribution.

## Q: What is scatter-gather?
**A:** Query sent to all nodes in parallel, results merged. Used without routing key.

## Q: Three properties of a good routing key?
**A:** High cardinality, even distribution, query pattern alignment.

## Q: What is a hotspot?
**A:** A node receiving disproportionately more traffic or data.

## Q: What is the skew factor?
**A:** max_size / avg_size - 1. Measures distribution imbalance.

## Q: What is the Saga pattern?
**A:** Distributed transaction pattern using compensating actions to undo previous steps on failure.

## Q: What is split-brain?
**A:** Multiple nodes think they're primary for the same data, causing inconsistency.

## Q: Two-phase commit (2PC)?
**A:** Prepare (all agree) → Commit (all commit) or Abort. Blocking protocol.

## Q: Client-side vs proxy routing?
**A:** Client-side: embedded, faster, needs updates. Proxy: centralized, transparent, adds hop.

## Q: When to avoid distributing data?
**A:** Data fits on single node, read-heavy, strong cross-node consistency needed.

## Q: What is rebalancing?
**A:** Moving data between nodes to maintain even distribution.

## Q: What is a composite routing key?
**A:** Multiple attributes used as routing key for flexible routing.

## Q: What is the PACELC theorem?
**A:** CAP extension: during partition trade-off A/C; else trade-off L/C.

## Q: Amdahl's Law for distribution?
**A:** Speedup = 1/((1-P) + P/N). Limited by non-parallelizable fraction.

## Q: What is geographic distribution?
**A:** Placing data in different regions to reduce latency for local users.

## Q: Distribution vs partitioning?
**A:** Partitioning splits within one database. Distribution splits across independent instances.
