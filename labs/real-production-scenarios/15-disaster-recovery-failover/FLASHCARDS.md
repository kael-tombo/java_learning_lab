# Lab 15 — Flashcards: DR Failover

| # | Front | Back |
|---|-------|------|
| 1 | RPO | Max acceptable data loss (e.g., 15 min) |
| 2 | RTO | Max acceptable downtime (e.g., 1h) |
| 3 | Backup/restore | Cheap, slowest RTO |
| 4 | Pilot light | Core on, scale at failover |
| 5 | Warm standby | Scaled-down live, fast scale-up |
| 6 | Active-active | Both serve; needs conflict handling |
| 7 | Failover | Push to secondary |
| 8 | Failback | Return to primary, merge care |
| 9 | Pre-failover check | Lag within RPO + secondary verified |
| 10 | Hold decision | Lag > RPO or unverified secondary |
| 11 | Replication lag metric | seconds_behind_master / replica lag |
| 12 | Backup age alert | age > RPO → page |
| 13 | 3-2-1 | 3 copies, 2 media, 1 offsite |
| 14 | Restore proof | Timed restore + app smoke test |
| 15 | DNS TTL | ≤60s for failover records |
| 16 | Split-brain | Two writers — block old primary |
| 17 | IC role | Single decision-maker |
| 18 | SEV-1 early | Declare before cutover debate |
| 19 | Cutover order | Stop writes → drain → promote → DNS → verify |
| 20 | Verify gate | Smoke test secondary pre-DNS |
| 21 | Schema drift | Flyway info both regions must match |
| 22 | Secret drift | Diff ConfigMaps/secrets cross-region |
| 23 | Conn strings | Parameterized per region |
| 24 | Idempotent migration | Safe replay via Flyway/Liquibase |
| 25 | IaC both regions | Same Terraform, no click-ops drift |
| 26 | Game-day cadence | Quarterly, timed, owned |
| 27 | RTO evidence | Measured drill total |
| 28 | RPO evidence | p99 lag + backup age |
| 29 | Queue drain | Drain Kafka/consumers before switch |
| 30 | Promotion cmd | RDS promote / PG pg_promote (see deep dive) |
| 31 | DNS cutover | Weighted / failover routing policy |
| 32 | Health check | Pre-staged, per-region probes |
| 33 | Status cadence | 10-min page, 15-min updates |
| 34 | Failback merge | Reconcile writes since failover |
| 35 | LWW | Last-writer-wins (conflict strategy) |
| 36 | CRDT | Conflict-free replicated type |
| 37 | Cost trade | Warm costs more, RTO lower |
| 38 | Load-test secondary | At 100%, not scaled-down guess |
| 39 | Chaos drill | Kill primary in staging, time TTD/TTM |
| 40 | TTD/TTM | Detect time / mitigate (promote) time |
| 41 | SLI readiness | Restore fresh + lag ok + drill current |
| 42 | Runbook must | Copy-paste cutover <30 min |
| 43 | Peer review | Missing DNS/secrets/queue step? |
| 44 | Tabletop | Talk-through before live drill |
| 45 | Comms template | Impact + RPO/RTO + ETA + next update |
| 46 | Data loss comms | State lag window honestly |
| 47 | Audit trail | All cutover cmds logged |
| 48 | Rollback of cutover | Revert DNS + demote if verify fails |
| 49 | Monitoring wall | Region health + lag + backup age |
| 50 | Owner + date | Next game-day on dashboard |
| 51 | Pilot scale time | Count in RTO (AMI + ASG warmup) |
| 52 | Backup encrypt | Encrypted + tested decrypt |
| 53 | Offsite copy | Different region/cloud |
| 54 | Retention | Sized to investigation + replay needs |
| 55 | App smoke | Login + checkout + read/write probe |
| 56 | Read-only mode | Degraded option while failing over |
| 57 | Write fence | `SET default_transaction_read_only` pre-promote |
| 58 | Promotion verify | New writes + lag zero + DNS |
| 59 | Post-mortem Q | Why did RTO/RPO slip? |
| 60 | Lesson | Untimed restore = assumed failure |
