# Time Ordering (Deep) - Real World Project

## Project: Ordering Guarantees for a Multi-Region Workflow Engine

### Objective
Make a workflow engine that spans three regions produce causally ordered state transitions
today, detect the ordering violations that already occur, and give operators a way to
replay history correctly.

### Why This Is a Real Problem
Workflow engines are the worst case for ordering: long-running steps, retries, compensating
actions, and multiple regions reading the same entity. A transition applied before its cause
is not a display bug — it produces states that the workflow never intended and that the
engine cannot recover from automatically.

### Architecture Overview
```
 Region A (writer)  ─┐
 Region B (writer)  ─┼─▶ transition log ─▶ ordered reducer ─▶ workflow state
 Region C (reader)  ─┘        │                    │
                              │                    ├─ idempotent step execution
                              │                    └─ causality violation metrics
                              └─ per-aggregate sequence + HLC envelope
```

### Phase 1: Detect the Existing Violations (Week 1)
1. Extract the last 30 days of transitions with their source region, HLC, and aggregate ID
2. Look for the concrete invariant: "no transition may be applied before its predecessor for
   the same aggregate" — count every breach and note the longest window
3. Cross-reference breaches against support tickets to quantify user-visible impact
4. If there are none, find the invariant that *is* being violated; if none exists, this
   project is premature and you should measure something else

### Phase 2: Choose the Ordering Mechanism Per Aggregate (Week 2)
1. Per-aggregate sequence number for intra-workflow ordering — cheap, exact, sufficient for
   most transitions
2. HLC on the envelope for cross-aggregate and cross-region reasoning, and for readable
   audit timestamps
3. A single-writer region per aggregate (routing by hash) so ordering is a routing property,
   not a protocol
4. Explicitly reject: relying on database timestamps, which are write-local and unrepeatable

**Do this:** route each aggregate to a home region. Most ordering problems disappear when
only one place can append to a given entity, and the remaining problem (cross-region reads)
is solved with HLC and lag monitoring.

### Phase 3: Implement Ordered Reduction (Week 3)
1. Every transition carries `(aggregateId, sequence, hlc, region, eventId)`
2. The reducer buffers out-of-order transitions per aggregate with a bounded window
3. Apply in sequence order; on window timeout emit a causality violation and apply the
   transition as a recovery step with an audit flag
4. Make step execution idempotent by `(workflowId, stepId, attempt-independent-key)`
5. Test: inject reordering and partition at every step; final state must be identical

### Phase 4: Cross-Region Reads (Week 4)
1. Regions read replicated state; measure and expose staleness as a first-class number
2. Reads that require current state get a consistency token from the home region
3. Reads that tolerate staleness (dashboards, history views) read locally and report the
   staleness age in the response
4. Never let a reader write back state it read staleley — route writes to the home region

### Phase 5: Replay and Operate (Week 5+)
1. Rebuild any aggregate's state from the transition log in sequence order — test it monthly
2. Dashboards: ordering violations per region, buffer occupancy, staleness age p99, replay
   divergence count
3. Alerts: any causality violation; staleness age above the documented threshold
4. Runbook: "workflow in unrecoverable state" — inspect transitions, replay, or apply a
   manual correction with an audited override

### Deliverables
1. Baseline violation report with user-visible impact quantified
2. Per-aggregate ordering envelope and the ordered reducer with bounded buffering
3. Idempotent step execution plus a replay-equivalence test
4. Staleness instrumentation, dashboards, and the recovery runbook

### Success Criteria
- Zero undetected out-of-order transitions on the chosen invariant
- Replaying any 30-day window reproduces byte-identical aggregate state
- Cross-region read staleness stays under the documented threshold at p99
- Every unrecoverable workflow surfaces within one window timeout

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Apache Kafka Documentation, "Message Delivery Semantics" —
  https://kafka.apache.org/documentation/#semantics
  Use for: the per-partition ordering guarantee and the fact that ordering scope is chosen by
  the producer's key. This is the mechanism behind routing each aggregate to a home region
  or a single partition. Pin to your broker version.
- Apache ZooKeeper Programmer's Guide —
  https://zookeeper.apache.org/doc/r3.9.2/zookeeperProgrammers.html
  Use for: the ordering guarantees ZooKeeper provides (total order via zxid) and the explicit
  statement that a client's view can be stale while it holds a valid session. The staleness
  argument for cross-region reads depends on this distinction.

### Estimated Time
6-7 weeks part-time