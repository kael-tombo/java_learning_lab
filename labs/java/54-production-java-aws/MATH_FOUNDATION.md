# MATH_FOUNDATION — AWS sizing & cost

## 1. Node sizing (Graviton JVMs)

Per-pod request/limit from lab-53 memory math; nodes sized so
`Σ pod limits + DaemonSets + 15% headroom ≤ node allocatable`. Graviton
(r/c/m7g) typically 15–25% cheaper per vCPU with equal-or-better JVM
throughput (G1/ZGC are arch-neutral) — re-run the lab-53 benchmark on
both families before committing; crypto-heavy paths differ most.

## 2. Aurora capacity math

Writer + N readers; failover RTO ~30–60 s (DNS + cache warm). IOPS:
provisioned vs I/O-Optimized break-even ≈ sustained > threshold in the
bill — compute from `VolumeReadIOPs + VolumeWriteIOPs` × price, not vibes.
PITR window (35 d max) bounds RPO ≤ 5 min only if transaction-log retention
covers it — verify with an actual restore drill (MINI_PROJECT).

## 3. Monthly cost shape

```
compute: nodes × hrs × price(Graviton) × utilization
+ ALB (LCU: new conns + active conns + bandwidth + rules)
+ Aurora (instance + storage + I/O) + ElastiCache (node-hrs)
+ MSK (broker-hrs + storage) or SQS (per-M requests + transfer)
+ CloudWatch (metrics + logs ingested + X-Ray traces)
+ ECR + data transfer (egress dominates APIs)
```

Tag every stack (service/env/owner); alert on week-over-week delta > 15%.

## 4. HPA arithmetic

Target pods ≈ peak RPS × p99 / (per-pod concurrency × target util).
Example: 2,000 RPS × 0.15 s / (200 × 0.7) ≈ 2.2 → 3 min (== AZ count),
max 20 for 10× spikes. Recompute quarterly — traffic shapes drift.
