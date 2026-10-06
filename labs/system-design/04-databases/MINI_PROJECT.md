# Database Design - MINI PROJECT

## Project: Multi-Tenant Order Database with Sharding and a Live Migration

**Time**: 8-12 hours

**Goal**: Take a single-table order schema, put it behind a shard router, and
migrate two columns to a new representation *without downtime and without
losing a row*.

### Starting Schema

```sql
CREATE TABLE orders (
  id            BIGSERIAL PRIMARY KEY,
  tenant_id     BIGINT      NOT NULL,
  status        TEXT        NOT NULL,
  subtotal_cents BIGINT     NOT NULL,
  tax_cents      BIGINT     NOT NULL,
  total_decimal  NUMERIC(12,2) NOT NULL,   -- legacy: money as decimal
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON orders (tenant_id, created_at DESC);
```

### Step 1: Build the Shard Router (2 h)

Implement `ShardRouter` from `CODE_DEEP_DIVE.md` with:
- SHA-256 based ring, 128 virtual nodes per shard.
- `shardFor(tenantId)` returning a shard id.
- A `verifyDistribution()` method that hashes 1,000,000 synthetic tenant ids
  and prints the imbalance factor. Target: under 1.05.

**Checkpoint:** imbalance factor reported and under 1.05. If it is not, you
have a bug — most likely a per-vnode salt that accidentally clusters points.

### Step 2: Tenant-Level Isolation (1 h)

Add `assertTenantVisible(queryResult, tenantId)` to every read helper. Then
deliberately write the bug: remove the assertion from one path, write a test
that proves tenant 7 can read tenant 9's order, and confirm the test fails.
That failing test is the deliverable — it is the regression guard.

### Step 3: Range Queries Without Scatter-Gather (2 h)

The access pattern is "latest N orders for tenant T". Because `tenant_id` is
the shard key, that query is single-shard by construction. Implement:

```java
List<Order> latestOrders(long tenantId, int limit);
```

Then add a query you *cannot* serve cheaply — `findAllOrdersAcrossTenantsSince(Instant)`
— and measure the fan-out cost on 8 vs 64 shards. Plot latency vs shard count
and annotate the linear region. This is the exercise that makes "no cross-shard
joins" concrete instead of a style rule.

### Step 4: Read Replica with a Consistency Pin (2 h)

Implement `ReadWriteRouter`. Write an integration test with a deliberately
lagging fake replica:

- Write an order, assert it is immediately readable (pinned to leader).
- Advance replica lag, write again, assert still correct.
- Advance replica past the write, assert reads now go to the replica.
- Assert `RateLimiter` for pinned reads never exceeds 10% of total reads.

### Step 5: The Zero-Downtime Migration (3 h)

Replace `total_decimal NUMERIC(12,2)` with `total_cents BIGINT`, and add
`status_changed_at TIMESTAMPTZ`.

```
EXPAND   -> add total_cents (nullable, no default) + status_changed_at
BACKFILL -> batched 1000 rows per statement, resumable from a checkpoint table
VERIFY   -> continuous diff job; alert if mismatch count > 0
SWITCH   -> new code writes both; reads from total_cents; 24h soak
CONTRACT -> drop total_decimal; gated on "no running query references it"
```

**Required**: the backfill must be *resumable*. Kill it halfway, restart, and
prove no rows were skipped and none were double-counted.

**Required**: a test that runs the full sequence against a production-shaped
fixture (1M rows) and reports per-phase duration. Contract phase must be
skipped by the test and gated by the access-log check instead.

### Step 6: Make It Observable (1 h)

Emit per-phase metrics: rows migrated per second, replication lag p99, pinned
read ratio, shard imbalance factor, slow-query count. Add one dashboard and
one alert on migration divergence.

### Deliverables

1. `ShardRouter` with a distribution test proving imbalance < 1.05.
2. Tenant-isolation guard plus the intentionally-broken regression test.
3. Cross-shard latency measurements at 8 and 64 shards with a written conclusion.
4. Resumable migration runner passing a 1M-row end-to-end test.
5. Read/write split with a consistency pin and a lag-driven test.
6. A short write-up: which migration step you think will break first in a real
   system, and why.

### Stretch

- Re-shard from 8 to 16 shards *live*, using the directory map to track moved
  keys and a dual-read verification window.
- Add a leader-follower failover with fencing tokens and fail the promotion if
  the node has not re-synced.