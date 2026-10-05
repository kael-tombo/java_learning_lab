# Lab 15 — Exercises: DR Failover

## Part A — Understand (1–15)
1. Define RPO/RTO for your service in one sentence each with numbers.
2. Map topology (backup/pilot/warm/active) to your cost vs RTO needs.
3. Measure replication lag for 24h; report p99 + max (RPO evidence).
4. Check backup age: `backup_age_hours` now? Alert threshold = RPO?
5. Time a restore to staging (stopwatch); compare to RTO.
6. Verify restored DB: row counts + app smoke test (not just "restore OK").
7. Diff primary vs secondary schema (`flyway info` both); fix drift.
8. Diff secrets/ConfigMaps across regions; list missing keys.
9. Check DNS TTL on failover records; lower to 60s if higher.
10. Draw cutover sequence: stop writes → drain lag → promote → switch DNS → verify.
11. Define failback steps (reverse) with data-merge caveat.
12. Write PromQL: `max(replication_lag_seconds) by (region)`.
13. Alert: backup job failure + age > RPO — test both fire.
14. Tabletop: region down 30 min — fail over or hold? Justify with lag number.
15. Draft SEV-1 comms for failover (status page + ETA cadence).

## Part B — Drill (16–30)
16. Planned failover in staging: time each phase, total vs RTO.
17. Simulate lag exceeding RPO; practice "hold + communicate" decision.
18. Break secondary (missing secret); show verification gate catches it pre-cutover.
19. Test split-brain guard: writes blocked on old primary after promotion.
20. Failback drill: return to primary without loss/duplicates.
21. Chaos: kill primary DB in staging; measure detection (TTD) + promotion (TTM).
22. Load-test secondary at 100% (not scaled-down guess) before relying on it.
23. Idempotent migration replay: run Flyway twice, prove safe.
24. Parameterize connection strings per region (no hard-code); verify switch.
25. Runbook timing: cutover commands all copy-paste, <30 min total.
26. Post-mortem one-pager for a 2h region incident.
27. SLI: DR readiness % (restore fresh + lag within RPO + drill current).
28. Cost RTO trade: price warm vs pilot-light vs backup-only.
29. Peer-review runbook for missing step (DNS? secrets? queue drain?).
30. Schedule quarterly game-day with owner + date on dashboard.

Stretch: active-active conflict resolution (CRDT / last-writer-wins audit) for one entity.
