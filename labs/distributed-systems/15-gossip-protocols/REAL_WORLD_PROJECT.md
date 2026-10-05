# Gossip Protocols - Real World Project

## Project: Gossip-Based Membership for a Multi-Region Service Registry

### Objective
Replace a periodically-refreshed service registry with gossip-based membership and SWIM
detection, so that node failures are detected in seconds instead of a refresh interval and no
registry component is a single point of failure.

### Why This Is a Real Problem
Polling-based registries have an unavoidable detection latency equal to their refresh interval,
and they scale their load linearly with fleet size. During a rolling deploy, dozens of nodes
arrive at once and the registry becomes the bottleneck — during exactly the window when it
matters most.

### Architecture Overview
```
  node-1 ─┬─ gossip ─ node-4 ─┬─ gossip ─ node-7
          │        (push/pull)│              │
  node-2 ─┴───────────────────┴─ gossip ─── node-8
      ▲                                          ▲
      └──────── SWIM failure detection ─────────┘
                    │
             Membership state: HEALTHY | SUSPECTED | DEAD
```

### Phase 1: Baseline the Current Detection (Week 1)
1. Measure current time-to-detect a dead node end to end — it is the sum of polling interval,
   threshold, and propagation, and it is almost certainly measured in minutes
2. Measure registry load at peak: requests/second, p99 latency, and CPU
3. Record how detection latency affected the last incident: how long did clients keep hitting
   a dead node?
4. Set the target: detection under 10 seconds, registry load independent of fleet size

### Phase 2: Implement Gossip Membership (Week 2)
1. Versioned per-node state: `(incarnation, status, metadata)` merged with max-wins
2. Gossip frequency tuned to hit the detection target with acceptable bandwidth — measure
   bytes/second/node at 10k nodes and confirm it is affordable
3. Random peer selection from the membership set; document how membership discovery itself is
   bootstrapped (seed nodes) and what happens if seeds are unreachable
4. Handle **incarnation numbers** correctly: they are what stops a resurrected node from
   confusing the cluster

### Phase 3: Add SWIM Detection (Week 3)
1. Direct probes at a short timeout
2. Indirect probes via k peers, with a longer timeout that accounts for the extra hop
3. Suspicion rather than immediate condemnation, with a refutation window
4. Refutation on receiving a suspicion about yourself, with a higher incarnation
5. Simulate a slow node and confirm refutation prevents its eviction

### Phase 4: Integrate with the Load Balancer (Week 4)
1. Registry states become routing decisions: `HEALTHY` → eligible, `SUSPECTED` → no new
   connections, `DEAD` → removed
2. Keep a connection-level circuit breaker underneath as a second line of defence
3. Propagate `SUSPECTED` quickly but keep serving existing connections — the graceful
   degradation step
4. Test: kill a node mid-request-storm and verify no new connections are routed to it

### Phase 5: Operate (Week 5+)
1. Dashboard: nodes by state, gossip bytes/second, probe success rate, suspicion rate,
   refutation rate, detection latency histogram
2. Alerts: any node in `SUSPECTED` beyond a few seconds, gossip loop stalls, refutation rate
   spiking (indicates network asymmetry)
3. Runbook: "false positive eviction" — check refutation rate and network asymmetry
4. Chaos: partition the cluster into halves and confirm each half still routes correctly
   within its own membership view

### Deliverables
1. Baseline detection-latency report with incident correlation
2. Gossip membership implementation with incarnation handling
3. SWIM detection with indirect probes and refutation
4. Load-balancer integration, dashboards, and the false-positive runbook

### Success Criteria
- Dead-node detection under 10 seconds at peak fleet size, measured
- Registry load does not grow linearly with node count
- Zero false-positive evictions under injected network asymmetry
- Each partition half routes only to nodes it believes are alive

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Apache Cassandra documentation, gossip and failure detection —
  https://cassandra.apache.org/doc/latest/architecture/assumptions.html
  Use for: the production statement of phi-accrual failure detection and the gossip-based
  failure detector Cassandra ships. Note the version-specific endpoint; confirm the page
  exists for the release you cite rather than assuming "latest" matches your deployment.
- Apache ZooKeeper Programmer's Guide —
  https://zookeeper.apache.org/doc/r3.9.2/zookeeperProgrammers.html
  Use for: the contrast case — ZooKeeper achieves ordering and liveness through a leader and
  a quorum rather than gossip. Useful when documenting why the registry needs consistency
  guarantees that pure gossip does not provide.

### Estimated Time
6-7 weeks part-time