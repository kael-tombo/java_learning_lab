# Lab 15 — Disaster Recovery Failover — Theory: Mechanics + Detection

## 1. DR Vocabulary
- **RPO** (max data loss, e.g., 15 min) vs **RTO** (max downtime, e.g., 1h). Backups serve RPO; automation serves RTO.
- Topologies: backup/restore (cheap, slow), pilot light (core always on), warm standby (scaled-down live), active-active (both serve).
- Failover (planned push to secondary) vs failback (return); both need rehearsal or DNS/data goes wrong.

## 2. Failure Mechanics
- Region loss: AZ outage → multi-AZ survives; region outage → DNS + cross-region replica decide fate.
- Data layer: async replication lag = potential loss (RPO gap); sync = zero loss but latency cost.
- Common DR fails: untested restore (corrupt/partial backup), DNS TTL 24h preventing cutover, schema drift between regions, missing secrets in secondary.
- Java specifics: connection strings hard-coded to primary; Flyway/Liquibase migration not idempotent on replay.

## 3. Detection
| Signal | Tool |
|--------|------|
| Region health (5xx/latency across AZs) | CloudWatch, Blackbox per-region probes |
| Replication lag (`seconds_behind_master`) | RDS/CloudSQL metrics, Kafka MM2 lag |
| Backup age/failure | Backup job status + `backup_age_hours` alert |
| DNS cutover readiness | Pre-staged health-checked records (Route53) |
| Restore test freshness | Last successful game-day date on dashboard |

## 4. Decision: Failover or Hold?
- Fail over when: primary region unhealthy >X min AND secondary lag within RPO AND app verified in secondary.
- Hold when: lag exceeds RPO (failover loses more than waiting) or secondary unverified — partial failover is worse.
- Declare SEV-1 early; single decision-maker (incident commander) avoids split-brain writes.

## 5. Prevention
- IaC both regions (same Terraform); secrets replicated; game-day quarterly with measured RTO/RPO.
- Backup 3-2-1 (3 copies, 2 media, 1 offsite); restore tested, not just backup green.
- DNS TTL ≤60s for failover records; runbook with copy-paste cutover commands.

## 6. Takeaway
DR is a tested procedure with numbers (RTO/RPO met last drill), not a document. If restore wasn't timed this quarter, assume it fails.
