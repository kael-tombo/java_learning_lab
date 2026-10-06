# Database Design - Code Deep Dive

Pure Java. Each section states the problem, the naive version, the fix, and the
residual risk.

## 1. Shard Router: hashing a key to a shard

```java
package systemdesign.databases;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.List;

/**
 * Consistent-hash sharding router.
 *
 * Why hash and not modulo? Modulo (key % n) remaps EVERY key when n changes.
 * Consistent hashing moves only ~1/n of keys per node change:
 *
 *   moved_fraction ~= 1 / n     (e.g. 16 shards -> 1 shard moved, ~6%)
 *   vs 100% for key % n
 *
 * We build a hash ring: each node owns (vnode, nodeId) points, sorted. A key
 * walks clockwise to the first vnode point.
 */
public final class ShardRouter {

    private final List<String> nodes;
    private final int virtualNodesPerNode;
    private final int[] ring;              // sorted array of hashes
    private final String[] ringOwners;     // parallel array

    public ShardRouter(List<String> nodes, int virtualNodesPerNode) {
        if (nodes.isEmpty()) throw new IllegalArgumentException("no nodes");
        this.nodes = List.copyOf(nodes);
        this.virtualNodesPerNode = virtualNodesPerNode;

        // 1. Place vnodes evenly around the ring. More vnodes -> finer grain,
        //    so rebalancing moves less data, at the cost of memory and lookup
        //    cost (O(log V) instead of O(log n)).
        int total = this.nodes.size() * virtualNodesPerNode;
        ring = new int[total];
        ringOwners = new String[total];
        int i = 0;
        for (String node : this.nodes) {
            for (int v = 0; v < virtualNodesPerNode; v++) {
                // Salt per vnode so vnode-0 and vnode-1 do not land adjacent.
                ring[i] = Math.abs((node + "#" + v).hashCode());
                ringOwners[i] = node;
                i++;
            }
        }
        sortRing();
    }

    private void sortRing() {
        Integer[] idx = new Integer[ring.length];
        for (int i = 0; i < idx.length; i++) idx[i] = i;
        java.util.Arrays.sort(idx, (a, b) -> Integer.compare(ring[a], ring[b]));
        int[] r2 = new int[ring.length];
        String[] o2 = new String[ring.length];
        for (int i = 0; i < idx.length; i++) { r2[i] = ring[idx[i]]; o2[i] = ringOwners[idx[i]]; }
        System.arraycopy(r2, 0, ring, 0, ring.length);
        System.arraycopy(o2, 0, ringOwners, 0, ringOwners.length);
    }

    /** Walk clockwise from the key hash to the first ring point. */
    public String shardFor(String tenantKey) {
        int h = Math.abs(keyHash(tenantKey));
        // Binary search for the first point >= h, wrapping to 0 at the end.
        int lo = 0, hi = ring.length - 1, found = ring.length - 1;
        while (lo <= hi) {
            int mid = (lo + hi) >>> 1;
            if (ring[mid] >= h) { found = mid; hi = mid - 1; } else lo = mid + 1;
        }
        return ringOwners[found];
    }

    private int keyHash(String key) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] d = md.digest(key.getBytes(StandardCharsets.UTF_8));
            // Take 4 bytes -> int. SHA-256 avoids String.hashCode collisions
            // and, more importantly, avoids a correlated hash family.
            return ((d[0] & 0xFF) << 24) | ((d[1] & 0xFF) << 16)
                 | ((d[2] & 0xFF) << 8) | (d[3] & 0xFF);
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }
}
```

**Residual risk:** a hash ring balances *key count*, not *load*. A single hot
tenant still melts its shard. Ring placement must therefore be driven by
observed QPS per tenant, with a manual override list checked before hashing.

## 2. Directory-Based Shard Map (the escape hatch)

```java
/**
 * Explicit key -> shard mapping. Use when the hash key is the wrong granularity.
 *
 * Trade-off: O(1) lookup and total control (you can pin a giant tenant to its
 * own shard), at the cost of a second data structure to keep consistent.
 * The directory is the single point of truth for ROUTING, never for DATA.
 */
public final class DirectoryShardMap {
    private final java.util.concurrent.ConcurrentHashMap<String, String> keyToShard =
            new java.util.concurrent.ConcurrentHashMap<>();
    private final java.util.Set<String> shards =
            java.util.concurrent.Set.of("shard-0", "shard-1", "shard-2", "shard-3");

    public String lookup(String key) {
        return keyToShard.get(key);               // null == not yet assigned
    }

    /** Idempotent assignment: assigning a key twice to the SAME shard is a no-op. */
    public boolean assign(String key, String shard) {
        if (!shards.contains(shard)) throw new IllegalArgumentException("unknown shard " + shard);
        String prev = keyToShard.putIfAbsent(key, shard);
        if (prev == null) return true;
        if (prev.equals(shard)) return true;      // idempotent retry
        throw new IllegalStateException("key already routed to " + prev);
    }
}
```

**Residual risk:** reassignment means a data move. Never "reassign" a live key;
dual-write, backfill, verify, then flip the directory entry.

## 3. Zero-Downtime Schema Migration (expand / migrate / switch / contract)

```java
/**
 * The four-phase migration runner.
 *
 * Invariant: at every instant, the OLDEST deployed binary must be able to
 * read and write the schema. That single constraint generates all four phases.
 */
public final class MigrationRunner {

    enum Phase { EXPAND, BACKFILL, SWITCH, CONTRACT }

    // EXPAND: additive only. New nullable column with a DEFAULT is instant in
    // modern engines; adding a column WITH a non-volatile DEFAULT rewrites the
    // table on old engines. Expand first, backfill second, never together.
    static final String EXPAND_SQL =
        "ALTER TABLE orders ADD COLUMN total_cents BIGINT NULL";

    // BACKFILL: never one big UPDATE. Batched by primary key so each statement
    // is short, does not bloat WAL, and holds no long row locks.
    static final String BACKFILL_SQL =
        "UPDATE orders SET total_cents = subtotal_cents + tax_cents " +
        "WHERE id > ? AND id <= ? AND total_cents IS NULL";

    // SWITCH: new code writes BOTH, reads NEW. Old code writes old only.
    // The dual write is temporary and must carry a removal ticket.
    static final String DUAL_WRITE_SQL =
        "UPDATE orders SET total_cents = ?, legacy_total = ? WHERE id = ?";

    // VERIFY: continuous diff job. This is the step teams skip, and it is the
    // step that turns a silent data loss into a caught error.
    static final String VERIFY_SQL =
        "SELECT count(*) FROM orders " +
        "WHERE (total_cents - (subtotal_cents + tax_cents)) <> 0 " +
        "  AND updated_at > now() - interval '1 hour'";

    /**
     * backfillInBatches — returns rows processed.
     * Batch size is a dial between lock duration and round-trip overhead:
     * start at 1,000, halve on lock-wait timeouts, double on clean runs.
     */
    static long backfillInBatches(java.sql.Connection c, long maxId, int batchSize)
            throws java.sql.SQLException {
        long total = 0;
        for (long lo = 1; lo <= maxId; lo += batchSize) {
            try (java.sql.PreparedStatement ps =
                     c.prepareStatement(BACKFILL_SQL)) {
                ps.setLong(1, lo);
                ps.setLong(2, lo + batchSize - 1);
                ps.setQueryTimeout(5);            // bounded statement, not a hope
                try (java.sql.ResultSet rs = ps.executeQuery()) { rs.next(); }
            }
            total += batchSize;
        }
        return total;
    }
}
```

**Residual risk:** CONTRACT drops old columns and *irreversibly* deletes data.
Gate it on a query against `pg_stat_statements` / the access logs proving no
running binary references the old name — never on "it's been two weeks".

## 4. Read/Write Split with a Consistency Pin

```java
/**
 * Route reads to replicas, but pin a user's own reads to the leader until
 * their write is visible. This is "read your own writes", implemented with a
 * session token rather than with a global wait-for-quorum (which would make
 * every read pay the replication delay).
 */
public final class ReadWriteRouter {
    enum Target { LEADER, REPLICA }

    // Stand-in for the DB's replication log position (LSN / GTID / binlog pos).
    public record Position(long lsn) {}

    private volatile Position leaderLsn = new Position(0);
    private final java.util.function.LongSupplier replicaLsn;

    public ReadWriteRouter(java.util.function.LongSupplier replicaLsn) {
        this.replicaLsn = replicaLsn;
    }

    /** Called after a successful write: remember how far we got. */
    public void noteWrite(Position at) {
        leaderLsn = at;
    }

    /**
     * Decide where to read. If the caller's last write is ahead of what any
     * replica has, the replica WOULD serve stale data, so go to the leader.
     * Compare-and-retry (bounded) covers the race where the replica catches up
     * between the check and the query.
     */
    public Target choose(boolean hasUnconfirmedWrite, long readAtLsn) {
        if (!hasUnconfirmedWrite) return Target.REPLICA;
        return replicaLsn.getAsLong() >= readAtLsn ? Target.REPLICA : Target.LEADER;
    }
}
```

**Residual risk:** this makes the *hot path* of every user who just wrote
something hit the leader. That is a real capacity cost. Measure the ratio of
pinned reads; if it exceeds a few percent, your writes are not batching, and
the problem is upstream.

## 5. Leader-Follower Failover (real, and honest about the split-brain)

```java
/**
 * Failover with a fencing token. The OLD leader is not trusted on return:
 * it must rejoin and re-sync. Without fencing, an old leader that was merely
 * partitioned will happily serve stale reads while the new leader serves new
 * ones, and the application will see time travel.
 *
 * token increments on every leadership change; the storage layer rejects any
 * write with a token lower than the highest it has seen.
 */
public final class LeaderFailover {
    private final java.util.concurrent.atomic.AtomicLong epoch =
            new java.util.concurrent.atomic.AtomicLong(1);
    private volatile boolean healthy = true;

    public synchronized long becomeLeader() {
        if (!healthy) throw new IllegalStateException("node unhealthy; cannot take leadership");
        return epoch.incrementAndGet();     // fencing token
    }

    public void markUnhealthy() { healthy = false; }

    public void rejoin() {
        // Must: snapshot from the new leader, discard local writes, THEN become
        // eligible. A node that has not re-synced must never be promoted.
        healthy = true;
    }
}
```

**Residual risk:** synchronous replication is the only way to avoid data loss
at failover, and it costs you the slowest replica's write latency on every
write. That is a real business decision, not a technical detail — take it
explicitly.