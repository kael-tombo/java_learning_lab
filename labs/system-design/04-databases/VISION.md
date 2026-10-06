# Database Design - Vision

## Why This Lab Exists
"Should this be SQL or NoSQL?" is the wrong opening question and it costs teams
weeks. The right question is *who owns the data, how is it partitioned, and
what must a reader see after a write*. This lab exists so the data model and
its physical layout are designed together, from evidence, before the ORM is
chosen.

## The Mental Model
A database design is three decisions stacked:

```
  1. Logical model   -> entities, access patterns, invariants
  2. Physical layout  -> partitioning key, index, storage engine
  3. Distribution      -> sharding, replication, routing
```

Each layer constrains the next, and the expensive mistake is discovering in
production that layer 1 assumed a join that layer 3 cannot perform.

## The Questions That Decide Everything
- What is the **primary access pattern**? The partitioning key must serve it.
- What is the **cardinality** of the chosen key? Too low = hot shard.
- What must be **transactional together**? That boundary becomes a service
  boundary in a distributed system.
- What is the **growth vector**? One tenant, one region, one entity type.
- What is the **read/write ratio**? It picks replicas vs. shards.

## The Five Things Everyone Gets Wrong
1. Sharding before you need it, on a key you cannot predict.
2. `UNIQUE` constraints that only exist in application code.
3. Cross-shard joins assumed to be "optimised later".
4. Sequences/IDs that leak volume and become a hotspot.
5. Schema changes done as a stop-the-world migration.

## What You Should Be able To Do
- Pick a shard key from access patterns and prove it with a distribution table.
- Design a schema migration that is backward compatible for one full release.
- Choose leader-follower vs. multi-leader vs. leaderless for a stated workload.
- Model multi-tenancy and say what leaks money when you get it wrong.
- Read a query plan and name the three most likely fixes.

## The Anti-Goals
- Not database-vendor advocacy.
- Not "eventual consistency is fine" — say *fine for which read*.
- No schema change that cannot be rolled back while old code is still running.

## Success Criteria
You can hand over a schema with: partitioning key and distribution evidence,
index justification, migration plan with dual-write/verify/cutover, and a stated
set of queries that are explicitly unsupported.

## How To Use This Lab
1. `THEORY.md` for multi-tenancy, sharding, replication, migrations.
2. `MATH_FOUNDATION.md` for hot-shard math, fan-out cost, replication lag.
3. `CODE_DEEP_DIVE.md` for a sharding router, migration runner, read/write split.
4. `MINI_PROJECT.md` to shard and migrate a real schema.
5. `REAL_WORLD_PROJECT.md` for a multi-tenant SaaS data layer.