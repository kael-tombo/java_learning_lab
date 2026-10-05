# Lab 15 — Math Foundation: RPO/RTO

## 1. RPO From Lag Distribution
- RPO met iff `p99(replication_lag) + backup_interval < RPO`. Lag p99 5 min + hourly backup → worst loss ~65 min > 15-min RPO → fails.
- Need: continuous log shipping (lag ~seconds) + frequent snapshots to hit RPO 15 min.
- Evidence: 24h lag histogram; report max, not mean — tail decides loss.

## 2. RTO Budget Decomposition
- `RTO_total = T_detect + T_decide + T_promote + T_dns + T_verify + T_scale`.
- Example: 5 + 10 + 5 + 2 + 10 + 15 = 47 min < 60-min RTO. Any phase slipping 15 min breaches.
- DNS: TTL 60s → ~2 min propagation p99; TTL 24h → RTO impossible. Math forces low TTL.

## 3. Availability From Topology
- Single region `A=99.9%` (~8.8h/y downtime). Active-passive with failover success `f=0.95`: `A ≈ 1 − (1−A1)×(1−f×A2)` ≈ 99.995% if secondary ready.
- If game-day stale (f=0.5): improvement halves. Readiness probability multiplies hardware redundancy.
- Active-active `A = 1 − (1−A1)(1−A2)` ≈ 99.9999% but conflict cost — only if merge logic proven.

## 4. Backup Frequency vs Loss
- Hourly snapshots: expected loss on crash ≈ 30 min avg, 60 max. For RPO 15 min need ≤10-min log shipping + 15-min snapshots.
- Storage cost linear in frequency × retention; loss cost stepwise (contract penalties). Optimize where marginal backup cost = marginal loss risk.

## 5. Queue Drain Time
- Kafka backlog B=500k, drain spare S=2k/s → `T_drain = B/S = 250s`. Must fit in RTO decide-phase or cut over with lag (accept loss).
- If `T_drain > RTO_remaining`, choose degraded cutover (read-only first) rather than waiting.

## 6. Worked Example
- RPO 15 min, RTO 1h. Lag p99 2 min, snapshots every 10 min → worst loss ~12 min ✓. Drill: 5+8+4+2+8+12=39 min ✓. Both met with margin; publish numbers, re-drill quarterly or decay assumed.
