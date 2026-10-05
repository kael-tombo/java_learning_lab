# Lab 15 — Real-World Project: Region Failover War Room

## Incident Timeline (Region Outage)
| Time | Event |
|------|-------|
| T+0 | Primary region probes red (5xx 100%, 3 AZs); replica lag 95s (within 15-min RPO) |
| T+4m | SEV-1 declared; IC assigned; status "Major incident: regional failure, evaluating failover" |
| T+10m | Gates pass: lag <RPO, secondary smoke green, backup 40 min old; decision: FAIL OVER |
| T+12m | Writes fenced on old primary; consumers drained (Kafka lag noted separately) |
| T+16m | Replica promoted (timeline 14); write probe `dr_probe` succeeds |
| T+18m | DNS failover flipped (TTL 60); waiting propagation |
| T+22m | Health green in secondary; p99 recovering; status "Traffic serving from secondary" |
| T+45m | Full verify: orders count ± lag window, logins OK, webhooks replayed |
| T+3h | Stable; failback scheduled next window with merge plan |
| T+2d | Post-mortem: RTO 45/60 min ✓, RPO 95s/15 min ✓; gaps closed |

## War-Room Runbook
1. **Assess** (5 min): region red? lag within RPO? secondary verified? One page with three numbers.
2. **Decide**: IC says FAIL OVER or HOLD with reason logged; no split-brain debates in channel.
3. **Fence + drain**: read-only old primary, drain queues, note lag window for comms.
4. **Promote + DNS**: copy-paste sequence; start RTO stopwatch.
5. **Verify**: write probe + row counts + smoke (login/checkout) before All-clear.
6. **Failback later**: re-sync, flip, verify; never rush back same night.

## Metrics That Matter
- TTD: region-red <5 min. Decision <10 min. RTO total vs 60 min. RPO lag vs 15 min.
- Secondary smoke pass/fail; DNS propagation p99; write-probe latency.
- Data-loss window stated honestly (lag seconds at promotion).
- Drill freshness: days since last timed restore/cutover (alert if >90).

## Prevention Backlog
- [ ] TTL 60 on failover records; pre-staged health checks.
- [ ] Lag + backup-age + drill-freshness dashboard with alerts.
- [ ] IaC parity + daily secret/schema drift diff.
- [ ] Quarterly game-day (timed) + tabletop for new joiners.
- [ ] Idempotent migrations; parameterized conn strings; read-only degraded mode.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- AWS disaster recovery options (backup/pilot/warm/active): https://aws.amazon.com/disaster-recovery/
- PostgreSQL continuous archiving / point-in-time recovery: https://www.postgresql.org/docs/current/continuous-archiving.html
- Kubernetes multi-cluster / federation patterns: https://kubernetes.io/docs/concepts/cluster-administration/federation/
