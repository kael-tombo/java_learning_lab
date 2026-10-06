# Database Design - Math Foundation

All numbers here are the ones you will be asked to defend in a design review.

## Hot Shard Probability (Zipf)

Request keys are not uniform. For a Zipf(s) distribution over N keys:

```
P(rank <= n) = H_n,s / H_N,s          H_n,s = sum_{i=1..n} i^(-s)

Fraction of traffic hitting the hottest k shards:
  share(k) = sum_{i=1..k} i^(-s) / sum_{i=1..N} i^(-s)
```

Worked example — 1,000,000 URLs, s = 1.2:
```
share(1)  ~ 15.6%      -> a single shard takes 1/6 of ALL writes
share(10) ~ 42%
share(50) ~ 66%
share(1%) ~ ~93%
```
**Lesson:** one hot key beats any amount of extra hardware. Fix it with a
replica-per-key / per-key fanout (push to read replicas or a dedicated
per-key store), not with more shards.

## Uniform Sharding Imbalance

With `n` shards and `k` keys routed by hash, each shard gets ~k/n keys.
Define the imbalance factor:

```
  imbalance = max_shard_load / (total_load / n)
  E[max]    ~ 1 + sqrt( 2 * ln(n) / k )      (extreme-value / Gumbel approx)
```

Example: k = 1,000,000 keys, n = 16 shards -> E[max] ~ 1.006, i.e. ~0.6%
over-average. Add virtual nodes and this is a non-issue. Human-chosen or
ranged keys have no such guarantee.

## Fan-Out Read Cost

A sharded query touching `f` shards costs roughly:

```
  cost(f) = f * (network RTT + per-shard planning + per-shard execution)
          ~= f * RTT   when f is large   -> latency grows LINEARLY with f
```

With RTT = 1 ms and f = 100 shards, a scatter-gather read is >= 100 ms before
doing any work. Mitigation order:
1. Scatter-gather in **parallel** -> latency ~ RTT, load ~ f (usually right).
2. Denormalise into a pre-aggregated read store.
3. Change the schema so the query is single-shard (best).

## Write Amplification

A single logical write replicated to `r` replicas, each with an index update
and a WAL flush:

```
  bytes_per_write = (record_size + index_delta) * (1 + r_sync)
  effective_durability_cost = r_sync * fsync_latency
```

Replication is not free at the storage layer either: a write to a
leader-follower pair moves the same pages twice unless the storage engine
itself is replicated.

## Read Replica Lag

Async replicas are consistent only after replication delay `D`. Under a burst
of `w` writes:

```
  D_burst ~= (w * bytes_per_write) / replica_throughput
```

Example: 5,000 writes/s * 2 KB = 10 MB/s of redo against a replica that can
sustain 6 MB/s -> lag grows without bound. The read replica silently becomes
the *oldest* copy. Always alert on lag, and never route a read-your-writes
request to a replica without a routing pin.

## Replication Lag Signal Quality

Lag is not one number — it is a distribution. Track:
```
  p50, p99, max over 60 s windows, plus a count of windows exceeding 5 s
```
Averages hide the replay-after-restart spikes where lag hits minutes.

## Distributed Transaction Cost

Two-phase commit adds at least one network round trip **per participant** and
holds locks for the whole protocol:

```
  T_2PC ~= T_coord + 2 * max_i(RTT_i) + sum_i(prepare_cost_i)
  Blocking window = duration of the slowest participant's decision
```
Worst case is unbounded: a participant crash after `PREPARE` blocks every
coordinator lock until the recovery timeout fires. That is the argument for
sagas + idempotent compensation (see lab 07-transactions).

## Multi-Tenancy Isolation Cost

```
  shared-everything:  cost_tenant = 1/N of the cluster (noisy-neighbour risk)
  shared-schema:      cost_tenant = 1/N + predicate overhead on every index scan
  schema-per-tenant:  cost_tenant = fixed_overhead / N  (connection + cache pressure)
  database-per-tenant:cost_tenant = dedicated (ops cost, lowest noisy-neighbour)
```
Rule of thumb from the numbers: below ~50 tenants, shared-schema; above
~10,000 with noisy neighbours, tiered (dedicated for the whales).

## Zero-Downtime Migration Cutover

Dual-write + verify + cutover has a bounded blast radius when the
incompatibility window is explicit:

```
  t_expand  -> new schema additive only, old code unaffected
  t_migrate -> backfill in batches, verify with a continuous diff job
  t_switch  -> new code reads/writes new; old code still reads old
  t_contract-> drop old only AFTER full release window has passed
```
The `t_contract` step must be gated on "no deployed binary references the old
column", not on a calendar date. Calendar-gated contracts are how outages
last three weeks.