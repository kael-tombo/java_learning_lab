# Distributed Database Design - Vision

## Why This Lab Exists
A single database server has a physical ceiling, and the ceiling arrives as an
outage you did not schedule. The question is never *whether* to distribute the
data layer, only *how* and *when* — and every "when" answer needs an arithmetic
justification, not a vibe. This lab exists to make distribution a deliberate
step with a reversible design.

## The Mental Model
Distribution is three decisions, and they are separable on purpose:

```
  1. PARTITION   -> which data lives where (a horizontal cut)
  2. REPLICATE   -> how many copies, and where (a redundancy cut)
  3. ROUTE       -> how a query finds its partition (a discovery cut)
```

Most "distributed database" pain comes from conflating them. You can shard
with no replicas (capacity, single point of failure). You can replicate with no
shards (read scale + failover, no capacity relief). Only when you need both do
you face the routing problem, which is the only genuinely hard part.

## Three Distribution Topologies
- **Vertical** — one machine, more RAM/disk. Buys time. Ceiling arrives fast.
- **Horizontal / sharded** — partition by key. Linear capacity, but every
  cross-shard query becomes a distributed query.
- **Federated / join-free** — separate stores per entity, joined in
  application. Maximal autonomy, and it moves joins into application code where
  they become N+1 queries. Know this trade before you choose it.

## The Questions That Decide the Design
1. What is the **single hottest query**? Its key becomes the shard key.
2. What is the **cardinality** of that key? One shard per *entity* vs one per
   *tenant* changes everything.
3. What is the **growth vector** — tenants, entities, or rows?
4. What must be **consistent**, and which read can tolerate staleness?
5. Can you **re-shard later**? If not, you are making a one-way door.

## What You Should Be able To Do
- Pick a shard key from access patterns and prove balance with a distribution
  table, including skew.
- Design replication topology (leader-follower, multi-leader, leaderless) for a
  stated workload and failure budget.
- Explain the routing layer and why a directory beats pure hashing for a moving
  dataset.
- Calculate the fan-out cost of a cross-shard query and design around it.
- Plan a re-shard with dual-write, verification, and a cutover.
- Say, with numbers, when *not* to distribute yet.

## The Anti-Goals
- Sharding for its own sake. A single Postgres with 2 TB and correct indexes
  beats an under-designed sharded cluster on every axis.
- Assuming the network is local. Every cross-partition call is a `p99` you do
  not control.
- Treating the replica set as a backup. Replicas replicate your mistakes.

## Success Criteria
You can produce a partition plan with: shard key, expected distribution and
worst-case skew, cross-shard query inventory with mitigations, replication
topology with RPO/RTO, and a re-shard procedure that can be executed while
traffic is live.

## How To Use This Lab
1. `THEORY.md` for the concepts and patterns.
2. `MATH_FOUNDATION.md` for skew, fan-out, and replication-lag arithmetic.
3. `CODE_DEEP_DIVE.md` for a router, directory map, and lag-aware read split.
4. `MINI_PROJECT.md` to shard, re-shard, and migrate a live schema.
5. `REAL_WORLD_PROJECT.md` for a multi-tenant data layer at scale.