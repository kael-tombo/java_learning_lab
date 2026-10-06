# Consensus - REAL WORLD PROJECT

## Project: Consensus-Backed Configuration Store for a Multi-Region Platform

**Time**: 3-4 weeks (team of 3)

**Scenario**: Your platform has 400 services, each with its own configuration
(feature flags, rate limits, routing rules, secrets references). Config changes
are currently a git push plus a 40-service restart, which is slow, risky, and
impossible to roll back quickly. Design a store where the config change is
linearizable and auditable.

**The key discipline:** you are *not* going to build Raft. You are going to use
it — correctly, with the right guarantees per read path — and prove you
understand its limits.

### Step 1: Write the Consistency Contract Before Choosing Anything

Produce a one-page contract, reviewed by every consuming team:

| Operation | Consistency | Latency target | Why |
|-----------|-------------|----------------|-----|
| `GET /flags/{key}` (flags) | Stale, bounded 30 s | p99 < 5 ms | Flags are worthless if they lag badly |
| `GET /limits/{key}` (rate limits) | Stale, bounded 5 s | p99 < 5 ms | Tight bound; overshoot is the failure |
| `GET /routes/{key}` | ReadIndex (linearizable) | p99 < 20 ms | Wrong route = total outage |
| `PUT /routes/{key}` | Linearizable | p99 < 50 ms | Must not lose or reorder |
| `LIST /flags` | Bounded staleness | p99 < 50 ms | Bulk, tolerate lag |

**This table is the deliverable that matters most.** Every later decision is
justified by a row in it, and every team that later complains about staleness is
complaining about a row they agreed to.

### Step 2: Why Consensus Is Required At All (and Where It Is Not)

Write an explicit argument:

- **Consensus IS required** for route changes and anything whose inconsistency
  causes an outage. Two concurrent operators must not both believe they won.
- **Consensus is NOT required** for feature flags: a last-write-wins
  counter with a TTL is enough, and it costs a fraction of the write latency.
- **Consensus is NOT required** for read-heavy config: replicas + bounded
  staleness + a version number that clients can compare.

State the cost you are accepting: linearizable writes mean every write costs a
quorum round trip. Compute from `MATH_FOUNDATION.md` how long that is at your
RTT, and show that it fits the 50 ms target with headroom. If it does not fit,
say so now, before building.

### Step 3: Layered Architecture

```
Clients
  |
  v
Edge / regional read cache  (bounded staleness; serves the "stale" rows)
  |
  v
Consensus layer  (Raft group, 5 voters across 3 AZs)
  |
  +---> Apply to every node in order, emit watch events
  |
  v
Read-model cache (per-node in-memory, versioned, rebuilt on restart)

Keyspace partitioned into INDEPENDENT Raft groups by key prefix:
  route/*  ->  group A   (strict, small, low volume)
  limits/* ->  group B   (moderate volume)
  flags/*  ->  group C   (high volume, relaxed)
```
Multiple groups is how you scale consensus write throughput, since a single
leader is the bottleneck. Document the group count and the reason each exists.

### Step 4: Reads Done Properly

- **Linearizable read**: the `ReadIndex` path (heartbeat confirms leadership,
  then read local applied state). Never a lease-based read — your cross-AZ
  clocks are not synchronised and the consequences are a split brain on the
  route table.
- **Bounded-stale read**: serve the local applied state, and **return the
  applied index/version in a response header** so the staleness is *visible* to
  the caller rather than assumed. Add a `?min_version=` parameter for callers
  that need to block until they catch up after a write.

Required test: a client writes with ReadIndex-read-back and asserts it observes
its own write 100% of the time across 10,000 iterations.

### Step 5: Membership Change Without Downtime

Grow from 3 to 5 and shrink to 3 during a quarter, using joint consensus. Then:

- Add a 6th node in a new AZ and verify it joins as a **non-voting learner**
  first, catches up, and only then becomes a voter.
- Write the runbook for replacing a dead node: the new node must NOT be added
  by restarting it and hoping. Get the ordering wrong and you get a cluster
  that cannot form a majority.

**Deliverable:** a membership-change log with the term at each transition and
proof that no commit succeeded with a disjoint majority.

### Step 6: Observability (the thing that actually operates consensus)

```
raft_term                    current term, per group     -- jumps = elections
raft_leader                  who leads, per group
raft_commit_index            progress                     -- stuck = real incident
raft_applied_index_lag       applied vs committed         -- should be ~0
raft_election_count_1m       leadership churn             -- alert if > threshold
raft_heartbeat_rtt_p99       network health
raft_snapshot_bytes          log growth rate
raft_quorum_acks             are we near losing quorum?
```

Alert on **term churn** and **applied lag**, not on CPU. Write the alert
threshold from the observed baseline, and state the action in the runbook.

### Step 7: Failure Drills

1. **Kill 2 of 5 voters simultaneously.** Verify writes continue (majority of
   3 remains) and measure the latency increase. Verify reads do *not* silently
   fall back to stale on the linearizable path — they should error instead.
2. **Isolate the leader for 60 s.** Measure time to elect a new leader, count
   rejected writes, and confirm the old leader cannot commit anything after
   healing (this is the safety test from `MINI_PROJECT.md`, at production
   scale).
3. **Clock skew of 3 seconds on one node.** Verify lease-based reads would have
   returned stale data and that ReadIndex does not. This is the drill that
   justifies the ReadIndex decision.
4. **Disk fill on one voter.** Verify the node steps down rather than
   acknowledging writes it cannot persist.

### Deliverables

1. Consistency contract table, with reviewer sign-off from consumer teams.
2. Justification for where consensus is used and where it is deliberately not.
3. Multi-group layered architecture with per-group key prefixes.
4. Read-path implementation with a 10,000-iteration read-your-own-write test.
5. Membership-change log across a real 3 -> 5 -> 3 cycle with safety proof.
6. Full metrics set plus an alerting policy tied to runbooks.
7. Four drill reports with measured numbers and the runbooks they changed.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Contract | "Strongly consistent everywhere" | Per-key guarantees with justifications |
| Consensus scope | Applied to everything | Deliberately scoped, cost quantified |
| Reads | Lease reads on skewed clocks | ReadIndex, with the clock-skew drill |
| Membership | Restarted node, hoped for | Learner-first, joint consensus, logged |
| Operations | CPU alerts | Term churn and applied lag with runbooks |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Kubernetes documentation — *Consensus and leader election* concepts, including
  `Lease` objects and leader-election resource behaviour; the production
  pattern for using a consensus-backed lease as a lock/coordination primitive.
  https://kubernetes.io/docs/concepts/architecture/leases/
- Apache Kafka documentation — *KRaft* consensus internals and the controller
  quorum, a well-documented real-world Raft implementation whose operational
  notes (term, ISR, controller failover) are directly applicable here.
  https://kafka.apache.org/documentation/

Both describe consensus in production. Note the deliberate difference: Kafka
and Kubernetes both assume reasonably synchronised clocks within a failure
domain, which is exactly the assumption that makes lease-based reads workable
there and *not* safe for a cross-AZ route table. Re-verify the K8s Lease API
version before quoting field names.