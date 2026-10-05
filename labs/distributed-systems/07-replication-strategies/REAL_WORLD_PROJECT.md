# Replication Strategies - Real World Project

## Project: Replication Hardening for a Postgres-Backed Primary

### Objective
Take a database primary with one streaming replica and turn it into a system with declared
durability guarantees, verified failover, measurable lag, and a read path that degrades
predictably.

### Why This Is a Real Problem
Single-replica setups fail in one specific way: the replica is 400ms behind, nobody noticed,
and failover silently loses the last few hundred writes. Everything in this project exists to
make that impossible to be surprised by.

### Architecture Overview
```
        writes
          │
          ▼
  ┌───────────────┐   streaming replication    ┌──────────────┐
  │   Primary     │ ─────────────────────────▶ │  Replica     │
  │  (sync=off)   │      lag measured          │  (reads)     │
  └───────────────┘                            └──────────────┘
          │  promoted only if lag < RPO budget
          ▼
  New primary ── rebuilt replica ── old primary demoted
```

### Phase 1: Establish the Current Posture (Week 1)
1. Record replication lag percentiles (p50, p99, worst) over two weeks of normal traffic
2. Identify write bursts that spike lag: bulk loads, index builds, batch jobs
3. Confirm what is synchronous today — most deployments have `synchronous_commit = on`
   meaning "local disk only", which surprises people
4. Write the RPO in business terms: "we may lose N seconds of writes" and get sign-off

### Phase 2: Declare the Guarantees (Week 2)
1. Choose a sync mode per write class:
   - Financial/journaling writes → synchronous to at least one remote node
   - Analytics and audit appends → async, with lag alerting
   - Bulk loads → async, off-peak, with explicit lag pre-checks
2. Implement promotion gating: a candidate is only eligible if lag < RPO budget, else promote
   and accept the documented data loss in writing
3. Alert on lag: warn at 1s, page at 10s, block promotions beyond 30s

### Phase 3: Failover Without Human Heroics (Week 3)
1. Script promotion: fence the old primary first, then promote
2. **Fencing is the critical step.** Promoting without fencing gives you two primaries, and
   split brain on a database is an outage with a corrupted-recovery path
3. Wire the new primary's `primary_conninfo` to rebuild the old primary as a replica
4. Verify application reconnection: pooled connections must be recycled after promotion

### Phase 4: Rehearse (Week 4)
| Scenario | Expected | Verify |
|---|---|---|
| Hard kill of primary | promotion within RTO, lag within budget | no acknowledged write lost |
| Network partition primary↔replica | writes stop (fencing), no split brain | old primary refuses writes |
| Replica lag 20s | promotion blocked or loss declared | RPO decision recorded |
| Promotion during bulk load | lag spike visible, alerting fires | bulk job resumed correctly |

1. Run each scenario in staging, then once in production at a low-traffic hour
2. Record actual RTO and data loss against the declared RPO

### Phase 5: Operate (Week 5+)
1. Dashboards: lag by bytes and seconds, replication throughput, WAL generation rate,
   checkpoint distance
2. Alerts: lag thresholds, replica down, WAL archive failing (this silently breaks PITR)
3. Quarterly failover rehearsal with the on-call engineer, not by the person who built it
4. Runbook: "replica lag" and "unexpected promotion" with real commands

### Deliverables
1. Documented sync/async policy per write class with RPO/RTO statements
2. Fenced promotion automation and rebuilt-replica verification
3. Lag dashboards, thresholds, and the two runbooks
4. Rehearsal report with measured RTO and confirmed data loss against the RPO

### Success Criteria
- Acknowledged writes survive a hard primary kill within the stated RPO
- Split brain is impossible: the fenced node refuses all writes
- Promotion is automated, not manual, and completes inside the RTO
- Lag alerting has fired and been diagnosed at least once before a real incident

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Amazon DynamoDB Developer Guide, "Core components of Amazon DynamoDB" —
  https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html
  Use for: how a managed store expresses replication groups, read replicas, and global tables
  — a useful reference point for what guarantees you gave up by running your own primary.
- Kubernetes Documentation, "Cluster Architecture" —
  https://kubernetes.io/docs/concepts/architecture/
  Use for: the etcd-backed control-plane model, where quorum-based replication and fencing
  are handled for you. Useful in the ADR arguing for a managed store over self-run
  replication for anything but the primary transactional load.

### Estimated Time
5-6 weeks part-time