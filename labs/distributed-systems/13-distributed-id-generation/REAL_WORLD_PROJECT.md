# Distributed ID Generation (Deep) - Real World Project

## Project: A Cross-Region, Cross-Service Identifier Platform

### Objective
Stand up an ID service that issues globally unique, time-ordered IDs to every service in every
region, with a documented capacity model, a worker-ID leasing scheme, and metrics that prove
the uniqueness claim holds.

### Why This Is a Real Problem
"Each service generates its own IDs" is how a company ends up with a support ticket titled
"order 12345 does not exist." Centralising IDs seems obvious and is often the wrong call;
this project is about making the trade explicitly and then operating the choice.

### Architecture Overview
```
  Services (all regions) ─▶ ID service cluster (3+ nodes)
        │                          ├─ worker-ID lease (ZooKeeper/etcd, TTL)
        │                          ├─ Snowflake generator per node
        │                          └─ clock-skew guard against lease authority
        ▼
   IDs: {timestamp | worker | sequence}
        │
        ├─► DB primary keys (BIGINT)
        └─► Event envelopes (idempotency keys)
```

### Phase 1: Make the Centralisation Trade Explicitly (Week 1)
1. Write the two options: centralised ID service vs per-service generators with a shared
   worker-ID namespace
2. Centralised: simpler guarantees, one more network hop on every write, one more dependency
3. Distributed: no extra hop, but you must manage worker-ID allocation yourself
4. Decide based on your actual ID rate and your write path latency budget, not on principle
5. If ID rate is under ~10k/sec, the centralised option is almost always fine — measure

### Phase 2: Worker-ID Allocation (Week 2)
1. Lease worker IDs from a coordination service as ephemeral sequential nodes
2. Lease TTL and renewal interval: ratio of roughly 1:3
3. On lease loss, **stop issuing IDs immediately** rather than continuing with a worker ID
   that may be reassigned — this is the only way to prevent duplicates
4. Startup assertion: refuse to start without a valid lease
5. Add a clock check against the lease authority; refuse if skewed beyond tolerance

```java
void onLeaseLost() {
    issuing.set(false);                       // atomic stop, before anything else
    alert.page("ID worker lease lost on node " + id);   // this is an availability event
}
```
6. Test: kill the lease node, confirm the ID worker stops before a duplicate is possible

### Phase 3: Capacity and Limits (Week 3)
1. Compute and document: 1024 workers × 4096 seq/ms = 4.19M IDs/sec theoretical
2. Measure actual per-node throughput; find the real limit, not the advertised one
3. Add backpressure: reject with `503 ID_CAPACITY` rather than silently stalling
4. Alert on sequence exhaustion rate (seq resetting many times per second means near capacity)
5. Watch the timestamp budget: 41 bits of milliseconds is ~69 years from the epoch; verify
   the epoch choice will not outlive the deployment

### Phase 4: Observability and Proof (Week 4)
1. Metrics per node: IDs issued, sequence utilisation, clock skew vs authority, lease state
2. **Uniqueness proof:** a periodic job samples 1% of issued IDs and asserts global
   uniqueness against a store — this is your ongoing evidence, not a hope
3. Detect clock regressions as a metric with the drift value, before they cause a failure
4. Alert: any regression above tolerance, any lease state change, any duplicate detection

### Phase 5: Operate (Week 5+)
1. Capacity plan reviewed quarterly against actual peak rate
2. Runbook: "ID service unavailable" — cached ID blocks with a documented max batch size,
   because the correct fallback is degradation, not a dependency on a failing call
3. Chaos: partition the ID service and verify callers degrade per the runbook
4. Document the fallback and make sure it is exercised, not just written

### Deliverables
1. Architecture decision record with the centralisation trade and measured ID rate
2. ID service with worker-ID leasing, clock guards, and an immediate stop on lease loss
3. Capacity model with real measured throughput and backpressure behaviour
4. Uniqueness sampling job, dashboards, and the degraded-mode runbook

### Success Criteria
- Zero duplicate IDs across 90 days, verified by the sampling job
- Any clock regression is detected and alerted before IDs are affected
- Lease loss stops issuance within one renewal interval, proven by test
- Callers degrade gracefully for at least the runbook's stated window

### Sourced field notes (fetched Oct 2026 — verify before citing)
- RFC 9562, "Universally Unique IDentifiers (UUIDs)" —
  https://www.rfc-editor.org/rfc/rfc9562.html
  Use for: the normative UUIDv7 layout, the monotonicity method, and the security
  considerations around random bits. Cite this over any secondary description of UUIDv7.
- etcd Documentation, v3.5 —
  https://etcd.io/docs/v3.5/
  Use for: lease grant/keepalive/revoke semantics and the TTL contract used to allocate
  worker IDs. Verify TTL granularity and minimum values for your deployed version before
  committing to a renewal ratio.

### Estimated Time
5-6 weeks part-time