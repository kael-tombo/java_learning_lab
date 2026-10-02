# MATH_FOUNDATION — GCP sizing & cost

## 1. Autopilot vs Standard break-even

Autopilot: pay per pod request (CPU+RAM × time) — no node-binpacking
skill needed, premium per unit. Standard: pay per node — cheaper past
~60–70% sustained binpack, plus Spot/ARM mixing. Compute both from the
lab-53 load profile; spiky → Autopilot/Run, steady → Standard.

## 2. Cloud Run concurrency math

Cost ∝ instances × (memory × time); instances ≈ RPS × latency /
concurrency. Raising concurrency 10→80 cuts instances ~8× at same RPS —
virtual threads make this free headroom. Floor: minScale>0 instances bill
always (availability) vs 0 (cold starts) — price the trade with the
lab-53 cold-start formula.

## 3. AlloyDB/Cloud SQL + Pub/Sub shape

HA + PITR retention bounds RPO (verify by restore drill); read-pool
replicas divide read RPS linearly until primary write throughput caps.
Pub/Sub: ordering keys cap per-key throughput (single sequencer) —
partition hot keys by suffixing (user-123#chunk) or drop ordering where
order doesn't matter.

## 4. Monthly cost shape + labels

```
GKE (Autopilot pod-reqs or node-hrs) + GCLB (rules + data)
+ AlloyDB/SQL (instance + storage + backup) + Memorystore + Pub/Sub (ops + transfer)
+ Monitoring/Trace/Profiler (ingest + retention) + Artifact Registry
```

Label everything (service/env/owner); sustained-use + committed-use
discounts apply to the steady baseline — buy down only what Autopilot
data proves steady.
