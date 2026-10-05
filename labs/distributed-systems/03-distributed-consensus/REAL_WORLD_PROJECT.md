# Distributed Consensus - Real World Project

## Project: Running Consensus for a Small Key-Value Cluster's Metadata

### Objective
Deploy a real consensus-backed key-value store (etcd or ZooKeeper class) to hold a small
service's metadata, and harden it: quorum sizing, snapshotting, read consistency policy,
and a chaos plan that proves the data survives leader loss.

### Why This Is a Real Problem
Small systems deploy a single-node "highly available" coordinator and discover during an
incident that it was the only copy of a critical table. This project takes the boring path:
run a real quorum, size it properly, and rehearse failover before it is real.

### Architecture Overview
```
   Service A ─┐
   Service B ─┼──▶ etcd (3 nodes, one per failure domain)
   Service C ─┘         │
                       ├─ metadata: service registry, feature flags, leader lease
                       └─ sessions:   short-lived coordination keys
```

### Phase 1: Size and Place the Cluster (Week 1)
1. Quorum rule: `2f+1` nodes tolerate `f` failures — three nodes tolerate exactly one
2. Place each node in a separate failure domain; a cluster where two nodes share a rack
   has a quorum that is a lie
3. Storage: local SSD, not network storage. Consensus performance collapses on contended
   network disks; this is the single most common etcd misconfiguration
4. Size the disk for the compaction window you will actually set

### Phase 2: Configuration and Hardening (Week 2)
1. `--data-dir` on dedicated volumes; set `--auto-compaction-retention` deliberately
2. Set `--quota-backend-bytes` so a runaway keyspace cannot fill the disk
3. TLS between members with a real CA, not self-signed-per-node
4. Client TLS enabled; peer TLS required
5. Enable audit logging to a sink outside the cluster

### Phase 3: Client Integration Correctly (Week 3)
1. Sessions with leases: every service creates a lease, keeps it, and exits on revoke
2. **Key TTL for every ephemeral key.** An unleased key on a coordinator node is a memory
   leak that only disappears when that node restarts
3. Retry-on-`leader-not-available` for reads that can tolerate it; fail fast for the rest
4. Linearizable reads for leader-election and lock paths; serializable reads elsewhere
5. Watch out for the silent gap: if a client can miss a watch event, it must re-read on
   reconnect — a watch is not a durable log position

### Phase 4: Chaos Rehearsal (Week 4)
| Scenario | Expected behaviour | Measure |
|---|---|---|
| Kill leader node | election completes, ~1–2s write unavailability | p99 write latency spike |
| Network partition 1-2 | remaining 2 of 3 still write (quorum intact) | no data loss |
| Partition 2-1 | 2-node side keeps writes, 1-node side rejects | correct rejection |
| Disk fill on one node | that node leaves quorum; no writes | alert fires |
| Slow disk (>1s p99 fsync) | latency cliff, likely election storm | alert on fsync p99 |

1. Run each scenario during business hours, not at midnight
2. Record actual election time and unavailability window; compare against the runbook
3. Fix the runbook with real numbers, not estimates

### Phase 5: Operate (Week 5+)
1. Alert on: leader changes per hour, fsync p99, DB size vs quota, slow apply count
2. Backup via snapshot API to object storage; rehearse a restore quarterly
3. Version policy: read the release notes before upgrading one node at a time
4. Document: "coordinator unavailable" runbook — which features degrade, which must fail

### Deliverables
1. Three-node deployment across failure domains with TLS everywhere
2. Client library wrapper handling leases, retries, and read consistency explicitly
3. Chaos report with measured election times and unavailability windows
4. Snapshot backup plus a verified restore in a scratch cluster

### Success Criteria
- Losing one node causes no data loss and no lasting unavailability
- All keys in service use leases or have explicit TTLs
- Leader election completes within the runbook's stated window in every rehearsal
- A restore from snapshot brings a fresh cluster to identical state

### Sourced field notes (fetched Oct 2026 — verify before citing)
- etcd Documentation, v3.5 —
  https://etcd.io/docs/v3.5/
  Use for: the authoritative statements on quorum size (`2f+1`), lease semantics, snapshot
  and defrag procedures, and the client-side watch guarantees. Verify the exact tuning flag
  names against the version you deploy — defaults changed across 3.4/3.5.
- Kubernetes Documentation, "Cluster Architecture" —
  https://kubernetes.io/docs/concepts/architecture/
  Use for: etcd as the control-plane backing store and the explicit warning to keep a backup
  plan for it. This is the clearest statement in the ecosystem that the consensus store is
  the cluster's single source of truth.

### Estimated Time
5-6 weeks part-time