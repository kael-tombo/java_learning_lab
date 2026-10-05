# CAP Theorem - Real World Project

## Project: Session Store Migration with an Explicit CAP Budget

### Objective
Design and stage the migration of a session store from a single-node in-memory cache to a
partition-tolerant distributed cache, documenting the consistency trade at each step and
proving the trade with measured evidence before traffic moves.

### Why This Is a Real Problem
Most CAP "migrations" fail not because the theorem was misunderstood but because the
trade was never written down. Session loss during a partition is an outage that only
appears in the one region where your users are not looking.

### Architecture Overview
```
                        ┌──────────────────────────────┐
   App tier (N pods) ──▶│  Distributed KV (CP mode)     │
        │               │  • linearizable reads          │
        │               │  • majority quorum             │
        │               │  • 3 replicas, 1 per AZ       │
        │               └──────────────┬───────────────┘
        │                              │ async invalidate
        ▼                              ▼
   Local L1 cache              Session TTL sweeper (30 min)
   (AP, 5s TTL)
```

### Phase 1: Establish the Baseline (Week 1)
1. Instrument the current single-node store: hit ratio, p50/p99 read latency, evictions
2. Record the session-loss tolerance with the product owner — the number that gates
   everything else. Typical answer: "0.2% of logins may be asked to re-authenticate."
3. Build the CAP decision record:
   - Partition tolerance: **non-negotiable** (multi-AZ, network will partition)
   - Consistency: **CP**, because a session read must never return another user's session
   - Availability budget: 0.5% of reads may fail fast during a partition

### Phase 2: Build the Client Layer (Week 2)
1. Implement `SessionStore` interface with two implementations behind one factory
2. `LocalCacheSessionStore` — AP, per-pod L1 cache, 5-second TTL, bounded size
3. `ConsistentSessionStore` — CP, reads and writes go to the quorum path
4. Feature flag `session.store.mode` = `local` | `distributed`, default `local`
5. Shadow mode: run both, compare values, log every divergence with trace ID

### Phase 3: Prove the Failure Modes (Week 3)
1. Chaos test: kill AZ-3 leader mid-traffic, measure read failures against the budget
2. Chaos test: partition A/B, confirm CP path rejects rather than serving stale
3. Verify L1 never serves a session past its TTL after invalidation broadcast
4. Record actual availability loss vs the 0.5% budget in the decision record

### Phase 4: Rollout (Week 4)
1. Canary at 1% for 48 hours, watching divergence rate and re-auth rate
2. 10%, then 50%, then 100%, each gate a 24-hour soak
3. Automatic rollback if re-auth rate exceeds 3x baseline
4. Decommission the old store only after a full 30-day TTL cycle

### Phase 5: Operate (Week 5+)
1. Alert on quorum read latency p99 and on partition-open duration
2. Quarterly chaos re-run against the 0.5% budget
3. Document the runbook: "session store degraded" — what breaks, what users see

### Deliverables
1. CAP decision record with the budget, the measurement, and the sign-off
2. Both implementations plus the shadow-compare harness
3. Chaos test results with measured availability loss
4. Rollout plan with rollback triggers and a runbook

### Success Criteria
- Re-authentication rate stays within the agreed tolerance
- Availability loss during induced partitions stays under 0.5%
- Every divergence captured in shadow mode is explained
- Rollback exercised at least once before full rollout

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Amazon DynamoDB Developer Guide, "DynamoDB read consistency" —
  https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html
  Use for: the concrete split between strongly consistent and eventually consistent reads,
  including the capacity-unit price of each (strong = 1 unit, eventual = 0.5 unit). This is
  the production form of the CP/AP decision: you pay per read for consistency.
- Martin Fowler, "Microservice Trade-Offs" —
  https://martinfowler.com/articles/microservice-trade-offs.html
  Use for: the "inconsistency window" framing — a distributed read can land on a replica
  that has not yet seen your write, which is precisely the stale read the CP path refuses to
  return. Cite this when explaining why eventual consistency is a developer-visible cost.

### Estimated Time
5-6 weeks part-time