# Distributed File Systems - Mini Project

## Project: An Erasure-Coded Block Store with a Consensus Namespace

### Objective
Split data into blocks, encode them so any k of n blocks reconstruct the original, store them
across simulated nodes, and serve reads and writes through a metadata layer that survives
node loss.

### Requirements
1. `ErasureCodec` — split into k data + m parity blocks, reconstruct from any k
2. `DistributedFileSystem` — write, read, delete across nodes
3. `FileInfo` — immutable metadata with content hash and version
4. `MetadataStore` — consensus-backed namespace with atomic rename
5. Node-failure harness that kills up to m nodes and verifies reconstruction

### Steps

**Step 1: Split, encode, reconstruct**
```
 k = 3 data blocks, m = 2 parity blocks, n = 5 total
 durability: survive loss of any 2 of 5 nodes
 storage overhead: n/k = 5/3 ≈ 1.67x  (vs 3.0x for triple replication)
 read amplification: must fetch k = 3 blocks; partial-block cache makes this ~1x
```
Reconstruction is linear algebra over the encoding matrix. The trick that makes it work is
choosing a matrix whose any `k x k` submatrix is invertible — a Vandermonde or Cauchy matrix
gives this for free.

```java
byte[][] reconstruct(byte[][] available, int k, int total) {
    var positions = IntStream.range(0, total)
        .filter(i -> available[i] != null).limit(k).toArray();   // any k work
    if (positions.length < k) throw new UnrecoverableDataLoss(positions.length, k);
    var sub = selectRows(encodingMatrix, positions);
    var inverse = invert(sub);                                    // k x k inverse
    return multiply(inverse, gather(available, positions));        // original blocks
}
```
Test it exhaustively: for every combination of k surviving blocks out of n, assert
reconstruction equals the original. Missing one combination means a data-loss bug in
production.

**Step 2: Write path and the striping decision**
```java
void put(String path, byte[] data) {
    var blocks = codec.split(data, blockSize);
    var all = codec.encode(blocks);                               // k data + m parity
    for (int i = 0; i < all.length; i++)
        node(targetFor(path, i)).put(blockId(path, i), all[i]);
    metadata.commit(new FileInfo(path, sha256(data), codecLayout(), Instant.now()));
}
```
Commit metadata **only after** all blocks are durable. Committing first produces files that
point at blocks which were never written — unrecoverable, and invisible until a read.

**Step 3: Metadata with atomic rename**
```java
void rename(String from, String to, long expectedVersion) {
    metadata.transact(m -> {
        if (m.version(from) != expectedVersion) throw new ConcurrentModification(from);
        m.move(from, to);                                          // atomic within one txn
    });
}
```
Atomic rename is the file system primitive everything else assumes — file handles keep
referring to the same inode. Get it wrong and every consumer of `mv` is broken.

**Step 4: Client caching and the stale-handle problem**
```java
byte[] read(String path) {
    var cached = handles.get(path);
    if (cached != null && cached.version() == metadata.currentVersion(path))
        return cached.data();                                       // cache hit, validated
    var fresh = readBlocksAndReconstruct(path);
    handles.put(path, new Handle(fresh, metadata.currentVersion(path)));
    return fresh;
}
```
Cache validation against the metadata version, not a TTL. This is why file systems keep
metadata separate from data: the version check is cheap even when the data is terabytes.

**Step 5: Survive node loss**
```java
@Test
void survivesLossOfAnyParityCountNodes() {
    for (var lost : subsets(nodes, PARITY_COUNT)) {
        killAll(lost);
        assertThat(fs.read("/important.bin"))
            .as("lost " + lost).isEqualTo(originalData);
        heal(lost);
    }
}

@Test
void refusesRatherThanReturningCorruptData() {
    killAll(nodes.subList(0, DATA_COUNT));          // fewer than k survive
    assertThatThrownBy(() -> fs.read("/important.bin"))
        .isInstanceOf(UnrecoverableDataLoss.class);   // never silently wrong
}
```
That second test is the most important one in the lab. A file system that returns wrong bytes
is worse than one that admits it cannot serve the file.

**Step 6: Cost it out**
| Scheme | Space | Tolerates | Read amp | Write amp |
|---|---|---|---|---|
| replication 3x | 3.0x | 2 node losses | 1 | 3 writes |
| erasure k3m2 | 1.67x | 2 node losses | 3 (1 with partial cache) | 5 writes + compute |
| erasure k6m3 | 1.5x | 3 node losses | 6 | 9 writes |

More parity means less space and more tolerance, at a linear write cost. That is the
trade-off you are actually making.

### Deliverables
1. `ErasureCodec` with exhaustive reconstruction tests over all k-of-n combinations
2. `DistributedFileSystem` with a write path that commits metadata last
3. `MetadataStore` with version-checked atomic rename
4. Node-failure suite plus the data-loss cost table

### Extension (CHALLENGE)
Add partial-block caching so read amplification drops from k to ~1 on sequential reads, and
measure the memory cost against the hit rate.

### Estimated Time
5 hours