# Multi-Cloud - Real World Project

## Project: Provider Exit Drill for a Critical Service

### Objective
Establish how quickly a critical service could move to a second provider, prove the answer by
doing it, and use the result to decide whether continued multi-cloud investment is justified.

### Why This Matters
"Multi-cloud ready" is usually an aspiration with no evidence. Provider exit is a
low-frequency, high-consequence event — and the only way to know your exit time is to
practice it. Most teams discover their exit time is measured in quarters, not days.

### Architecture Overview
```
  Primary (AWS)                          Secondary (Azure)
  ┌────────────────────┐                ┌────────────────────┐
  │ Orders service     │                │ Orders service     │
  │ PostgreSQL ────────┼── CDC ────────▶│ PostgreSQL replica │
  └─────────┬──────────┘   replication  └─────────┬──────────┘
            │                                    │
       Object storage                     Object storage
       (portable API)                     (portable API)

  Domain core: shared library, no provider SDK imports
  CI: one pipeline, three provider targets
```

### Phase 1: Choose the Scope (Week 1)
1. Name the risk being mitigated: provider outage, regulatory residency, acquisition risk,
   or pricing leverage. Pick one and write it down
2. Decide which capability actually needs redundancy. Usually: *compute* is portable,
   *data* is not, so the exit is a data migration problem
3. Decide the target posture: active-active (expensive, true failover) or warm standby
   (cheaper, slower failover). Write down the RTO you are buying
4. Get the budget signed off for the standby environment, including the idle cost that never
   appears on a feature ticket

### Phase 2: Portable Core (Week 2)
1. Extract the domain logic into a library with zero provider dependencies, enforced by CI
2. Standardise persistence on PostgreSQL-compatible SQL where possible; where a provider
   feature is genuinely required, isolate it behind a port and document it as non-portable
3. Containerise everything with a standard base image and standard health endpoints
4. Standardise observability with OpenTelemetry so a failover does not lose telemetry
5. Identity: no portable story exists. Document per-provider identity mapping as a known cost

### Phase 3: Data Migration Path (Week 3)
1. Chose CDC from the primary database into the standby
2. Verify replication lag is bounded and alerted; define the RPO from the measured lag, not
   from hope
3. Document the schema compatibility envelope — the migration fails when the standby cannot
   read the primary's writes, and that is the most likely exit blocker
4. Test recovery point: truncate and restore, then measure the actual RTO

### Phase 4: The Drill (Week 4)
1. Deploy the identical image to the standby
2. Replicate data up to a known point
3. **Promote** the standby: cut over writes, redirect traffic
4. Measure: RTO (traffic-serving restored), RPO (data loss), operator effort
5. Write the timeline from the drill, including every manual step and how long it took

Be honest about the result. A drill that takes six hours and a runbook with nine undocumented
steps is the most valuable artefact this project produces.

### Phase 5: Decide and Maintain (Week 5+)
1. Write the decision: continue multi-cloud, reduce to warm standby, or consolidate to
   single-cloud with the standby environment decommissioned
2. If continuing: budget the carrying cost explicitly, including idle standby spend and the
   engineer-days per release for the adapter layer
3. Run the drill twice a year; a drifted standby fails at the worst moment
4. Track the deliverable that matters: *time to exit*, as a number, re-measured each drill

### Deliverables
1. Scope decision naming the risk, the redundancy target, and the RTO being bought
2. Portable core with CI-enforced provider independence, plus the non-portable inventory
3. CDC replication with measured lag and a verified recovery-point test
4. Drill report with real RTO/RPO, the full manual step list, and the go/no-go decision

### Success Criteria
- A full provider exit demonstrated end to end, with measured RTO and RPO
- Every manual step in the cutover documented with its duration
- The non-portable list is explicit and accepted by engineering leadership
- A recorded decision on continuing, reducing, or exiting multi-cloud

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Amazon CloudWatch documentation —
  https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html
  Use for: the maintained description of the provider monitoring primitives used in the
  portability assessment, and to document honestly which observability features do *not* port.
- Microsoft Learn, Azure Well-Architected Framework —
  https://learn.microsoft.com/en-us/azure/well-architected/
  Use for: the provider-neutral reliability and cost trade-off guidance used to structure the
  scope decision in Phase 1. Verify which pillars and principles are current.

### Estimated Time
10-12 weeks part-time