# Partitioning and Sharding - Mini Project

## Project: Three Sharding Schemes, One Skew Report

### Objective
Implement range sharding, hash sharding, and consistent hashing over the same keyspace, then
measure skew, remap cost, and query behaviour for each.

### Requirements
1. `RangeSharding` — sorted key boundaries, explicit ranges
2. `HashSharding` — `hash(key) mod N`
3. `ConsistentHashing` — hash ring with virtual nodes
4. `Rebalancing` — move data to new nodes with bounded concurrent transfers
5. `SkewReport` — max/mean load ratio and remap percentage per scheme

### Steps

**Step 1: Range sharding and its two skews**
```java
int shardFor(String key) {
    for (int i = 0; i < boundaries.size(); i++)
        if (key.compareTo(boundaries.get(i)) < 0) return i;
    return boundaries.size();
}
```
Two failure modes, both real:
- **Data skew** — a popular key range sends disproportionate load to one shard
- **Add skew** — new keys are always at the end, so the last shard absorbs all new inserts
  and the first shard never grows. Split the hottest range and rebalance.

**Step 2: Hash sharding distributes but cannot move**
```java
int shardFor(String key) { return Math.floorMod(key.hashCode(), shardCount); }
```
Perfect distribution, but changing `shardCount` from 8 to 16 remaps **~7/8 of all keys**.
Every node becomes a hot spot at once. Measure it:
```java
int moved(String oldFn, String newFn) {
    int n = 0;
    for (String k : keys) if (shardOf(k, oldFn) != shardOf(k, newFn)) n++;
    return n;
}
```

**Step 3: Consistent hashing remaps only the neighbourhood**
```java
Node locate(String key) {
    var entry = ring.ceilingEntry(hash(key));
    return entry != null ? entry.getValue() : ring.lastEntry();   // wrap around
}
```
Going from 4 to 5 nodes moves roughly `1/5` of keys, not `4/5`. Virtual nodes (say 200 per
node) smooth the load distribution so no node gets 2x the mean. Assert with a test that
max/mean < 1.3 across 100k keys.

**Step 4: Bounded rebalancing under live writes**
```java
void rebalance(List<Node> target, int maxConcurrentMoves) {
    var moves = planMoves(currentPlacement, target);       // {key, from, to}
    var pool = Executors.newFixedThreadPool(maxConcurrentMoves);
    for (var m : moves) pool.submit(() -> moveUnderLock(m));
    pool.shutdown();
    awaitQuiescence();
}
```
`moveUnderLock` must take a per-key lock so a concurrent write is not lost mid-move. Test it:
hammer writes during a rebalance and assert zero lost updates. This is the bug that makes
people afraid of rebalancing.

**Step 5: Query behaviour**
Implement:
- point lookup → always one shard
- range scan → range: one-to-many but efficient; hash: all shards + merge
- aggregate (`count where tenant = X`) → route by the filter if the shard key matches;
  otherwise scatter-gather across all shards

Add a scatter-gather query and measure fan-out cost. That number is why the shard key should
usually equal your primary filter.

### Deliverables
1. `RangeSharding`, `HashSharding`, `ConsistentHashing`, `Rebalancing`
2. `SkewReport` printing max/mean load and remap percentage for each scheme
3. Concurrent-write-during-rebalance test with zero lost updates
4. A decision note: which scheme for which access pattern, with your measurements

### Extension (CHALLENGE)
Implement directory-based sharding with dynamic shard-to-node mapping, so adding a shard is a
metadata change and adding a node is a data movement — then compare its operational cost to
consistent hashing.

### Estimated Time
3-4 hours