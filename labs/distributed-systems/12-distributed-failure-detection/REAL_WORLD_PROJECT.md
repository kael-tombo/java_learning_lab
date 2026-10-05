# Distributed Failure Detection - Real World Project

## Project: Tuning Failure Detection for a Live Service Mesh

### Objective
Replace blanket health-check timeouts across a running system with a detector whose
thresholds follow measured latency distributions and whose decisions are staged, so that
failover happens fast without evicting nodes that were merely slow.

### Why This Is a Real Problem
Most false-positive failovers are traced back to a threshold someone set as a round number
in a config file. The cost is real: a healthy node leaves the pool, in-flight work moves,
and the cluster absorbs a load spike at the worst possible moment.

### Architecture Overview
```
  Service A ──heartbeats──▶ Detector (phi, per-peer)
       ▲                        │
       │              SUSPECTED ─┴─▶ probe (cheap RPC)
       │                             │
       │                    CONFIRMED ─▶ remove from pool
       │                             └──▶ alert
       └── health-check interval, retries, timeout ──► configured from measured p99
```

### Phase 1: Measure the Real Latency Distribution (Week 1)
1. Collect heartbeat arrival intervals per peer for two weeks
2. Plot the distribution per peer, not the mean — variance is the whole story
3. Identify peers with bimodal distributions (those are the ones a fixed timeout will
   eventually wrong)
4. Record current false-positive failovers from incident history, if any exist

### Phase 2: Deploy a Detector in Shadow Mode (Week 2)
1. Run phi-accrual alongside existing health checks, evaluating but not acting
2. Log every verdict with the computed phi value
3. For each period where the detector says SUSPECTED but the node was healthy, capture why —
   GC, deploy, GC again? That profile drives the threshold
4. Choose the initial phi threshold from the shadow data and write down the cost arithmetic

### Phase 3: Stage the Decisions (Week 3)
1. `SUSPECTED` → stop assigning new work; keep existing connections
2. `CONFIRMED` requires either two consecutive failures or an independent probe failing
3. `HEALTHY` → return to the pool with a short probation period before full traffic
4. Add hysteresis: recovery threshold lower than failure threshold, so a flapping node does
   not thrash the pool
5. Every transition emits a metric; every CONFIRMED emits an alert with the phi trace

### Phase 4: Tune Per-Tier (Week 4)
Different tiers deserve different answers:
| Tier | Detection goal | Suggested setting |
|---|---|---|
| Stateless API replicas | fast eviction, tolerate false positives | aggressive phi, confirm on 2nd failure |
| Database primary | never falsely evict | conservative phi, never auto-failover |
| Batch workers | slow is fine | long interval, high phi |
| Cached metadata | fast, tolerate false positives | aggressive |

1. Set per-tier configuration and document the reasoning
2. Verify the database primary never auto-evicts: fail it to manual approval
3. Load-test a flapping node and confirm the pool does not thrash

### Phase 5: Operate (Week 5+)
1. Dashboards: phi distribution per tier, SUSPECTED/CONFIRMED rate, pool size over time
2. Alerts: CONFIRMED rate, pool size below desired, and "detector disagrees with health check"
3. Quarterly review of thresholds against new latency distributions
4. Runbook: "node repeatedly evicted" — check GC, deploys, and network, then the threshold

### Deliverables
1. Latency distribution analysis per peer with a recommendation per peer
2. Phi-accrual detector in shadow mode plus two weeks of verdict logs
3. Staged SUSPECTED/CONFIRMED/HEALTHY policy with hysteresis
4. Per-tier configuration table, dashboards, and the eviction runbook

### Success Criteria
- False-positive failovers reduced by at least 80% versus the baseline period
- True-failure detection latency stays within the agreed RTO contribution
- No thrash: pool size is stable under a deliberately flapping node
- Every tier has documented thresholds and an owner

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Kubernetes Documentation, "Leases" —
  https://kubernetes.io/docs/concepts/architecture/leases/
  Use for: the production parameters for lease-based failure detection — `leaseDurationSeconds`,
  `renewTime`, and the ratio between them that avoids both premature failover and missed
  detection. These are the closest maintained reference for tuning a detector's interval.
- Apache ZooKeeper Programmer's Guide —
  https://zookeeper.apache.org/doc/r3.9.2/zookeeperProgrammers.html
  Use for: the session/heartbeat model, the session timeout contract, and the explicit
  caveats about what a client can and cannot conclude from a lost connection. The
  "suspicion" discussion is the foundation phi-accrual detectors are built on.

### Estimated Time
5-6 weeks part-time