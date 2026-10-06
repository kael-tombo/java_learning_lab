# Distributed Database Design - MINI PROJECT

## Project: Shard a Working Schema, Then Survive a Re-Shard

**Time**: 10-14 hours

**Goal**: Take a single-node e-commerce schema, partition it, prove the
partition is balanced, then **re-partition from 4 shards to 8 while traffic is
flowing** — the thing nobody practises until they must.

### Step 1: Schema and Access Patterns (1 h)

Start with:

```sql
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL,
  customer_id BIGINT NOT NULL,
  status TEXT NOT NULL,
  total_cents BIGINT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL);

CREATE TABLE customers (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL,
  email TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL);
```

Enumerate your top 10 queries with a measured frequency. For this lab they are:

| # | Query | Freq | Shard-local? |
|---|-------|------|--------------|
| 1 | orders for tenant, latest page | 40% | yes, if tenant_id is the key |
| 2 | single order by id | 25% | **no** — id is global |
| 3 | customer by id | 15% | **no** |
| 4 | orders for customer | 10% | only if keyed by customer |
| 5 | tenant dashboard aggregate | 10% | yes |

**Checkpoint:** queries 2 and 3 are not shard-local. Do not "fix" this by
co-locating everything on tenant_id and pretending single-key lookups are free.
Write down how you will serve them and what it costs.

### Step 2: Partition Function + Balance Proof (2 h)

Implement the consistent-hash router from `CODE_DEEP_DIVE.md` (4 shards, 128
vnodes). Then write `verifyDistribution()`:

```
Generate 1,000,000 tenant_ids (Zipf s=1.0 AND uniform).
For each distribution:
  - print per-shard key count
  - print per-shard simulated QPS
  - print imbalance factor = max_shard_load / (total / n)
Target: imbalance < 1.05 under uniform, and an explicit, accepted number
under Zipf.
```

**Checkpoint:** under Zipf, one shard will be far above average. Do not paper
over it. Write the sentence: *"the hottest shard takes X% of load; we accept
it because..."* with either a mitigation (per-tenant replica) or a rejection.

### Step 3: The Two Non-Shard-Local Queries (2 h)

Query 2 (`order by id`) and query 3 (`customer by id`) need a strategy. Pick
one and implement it:

- **(a) Encode the shard in the id** (e.g. base-36 id whose prefix is the
  shard). Route without lookup. Write a `decomposeId()` and assert the routing
  is always correct for ids you generated.
- **(b) Global id index**: a small dedicated index table mapping `id -> shard`.
  Fast reads, one extra write per insert, and a second thing to shard.

Then serve query 4 (`orders for customer`) — decide whether to add a
secondary shard-local index and accept the write amplification, or to
document it as an accepted scatter-gather with a measured cost.

**Required:** measure the scatter-gather cost for query 4 across 4 and 16
shards, and plot it. Annotate where it stops being viable.

### Step 4: Re-Shard 4 -> 8 With Live Traffic (4 h)

The core exercise. Sequence:

```
1. Deploy new router code that knows about 8 shards but routes everything
   to the 4 old ones. (Backward compatible. No behaviour change.)
2. Enable DUAL WRITE: write to old shard AND new shard.
3. Run a continuous verification job comparing old vs new for the last hour.
4. Backfill historical rows into new shards in batches, resumable.
5. Flip the directory: new reads/writes go to 8 shards.
6. Run DUAL READ (new first, fall back to old) for 24 h, logging fallbacks.
7. Stop dual write. Leave old shards read-only for one more release.
8. Drop old shards.
```

Required tests:

- Kill the process during backfill. Restart. Assert zero rows missing and zero
  rows duplicated.
- Inject a verification mismatch. Assert the migration halts rather than
  proceeding to step 5.
- Measure and report: time per phase, throughput, and rows moved.

**This exercise is the whole lab.** Everything else is setup.

### Step 5: Read Replicas with a Consistency Pin (2 h)

Add one replica per shard. Implement the lag-aware read split from
`CODE_DEEP_DIVE.md`, then assert with a lagging fake replica:

- A write followed immediately by a read returns the written value 100% of the
  time.
- After lag catches up, reads actually go to the replica (assert the routing
  decision, not just the result).
- Pinned reads never exceed 10% of total reads.

### Step 6: Observability (1 h)

Metrics: per-shard key count, per-shard QPS, imbalance factor, cross-shard
query count, replica lag p50/p99, migration phase progress, verification
mismatch count, and rows-moved-per-second during the re-shard.

One alert that matters: **imbalance factor > 1.5** — that is a routing bug or a
hot key, and it is silent otherwise.

### Deliverables

1. Access-pattern inventory marking which queries are shard-local.
2. Partition function with a distribution report for uniform and Zipf loads.
3. Decision + implementation for the two non-shard-local queries.
4. A completed live re-shard from 4 to 8 shards with per-phase timings and the
   three required tests.
5. Replica routing with a consistency pin and a lag-driven test.
6. Metrics dashboard and the imbalance alert.
7. A written verdict: would you have sharded at all at 10% of this dataset
   size? Show the numbers that support your answer.

### Stretch

- Implement a single-key failover: promote a replica on primary loss, with a
  fencing token so the old primary cannot resume writes. Verify zero split
  brain.
- Add a global secondary index for `customer_id` and measure the write
  amplification you introduce.