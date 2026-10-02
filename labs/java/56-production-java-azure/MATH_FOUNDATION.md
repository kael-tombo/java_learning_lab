# MATH_FOUNDATION — Azure sizing & cost

## 1. AKS node math (same physics, Azure prices)

`Σ pod limits + DaemonSets + 15% headroom ≤ allocatable`; ARM (Cobalt/
Ampere) pools for JVMs where supported — same benchmark-first rule as
Graviton (crypto paths differ most). Spot node pools for batch/fault-
tolerant workers only, never the serving path (eviction math: savings ×
(1 − P(evict during peak)) must stay positive).

## 2. Flexible Server HA + PITR

Zone-redundant standby, failover RTO in minutes; backup retention window
bounds RPO — verify with the restore-into-new-server drill (canary diff),
not the portal blade. IOPS tier (provisioned vs same-zone trade) from
measured `read/write_iops`, not instance size.

## 3. Service Bus vs Event Hubs sizing

Service Bus: throughput units / premium messaging units per namespace;
sessions serialize per session (hot-session ceiling mirrors ordering-key
math). Event Hubs: throughput units (ingress MB/s + events/s); capture
adds storage cost linearly. Hot session/key? Shard or drop ordering —
same answer, third cloud.

## 4. Monthly cost shape + reservations

```
AKS (node-hrs/spot mix) + App Gateway (fixed + capacity units)
+ Flexible Server (compute + storage + backup) + Redis + SB/EH (units + ops)
+ Monitor/Insights (ingest + retention) + ACR + egress
```

Tag (service/env/owner); reservations + saving plans only on the
Autopilot-equivalent proven-steady baseline — measured, not hoped.
