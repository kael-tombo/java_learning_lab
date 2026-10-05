# Lab 15 — Code Deep Dive: Backup/Restore + Failover Runbook

## 1. Backup Drill (Postgres Example)
```bash
# Nightly base + WAL shipping assumed; verify age
pgbackrest info --stanza=prod | grep -E "backup|time"
# Age alert (Prometheus): time() - pgbackrest_last_backup_timestamp > 16*3600
# Manual base backup
pg_basebackup -h primary.db -U repl -D /backups/$(date +%F) -Ft -z -P
ls -lh /backups/ && sha256sum /backups/$(date +%F).tar.gz > /backups/checksums.txt
```

## 2. Timed Restore to Staging
```bash
time {
  rm -rf /var/lib/postgresql/staging && mkdir -p /var/lib/postgresql/staging
  tar -xzf /backups/2026-10-04.tar.gz -C /var/lib/postgresql/staging
  pg_ctl -D /var/lib/postgresql/staging start
  psql -h localhost -U app -d app -c "SELECT count(*) FROM orders; SELECT max(updated_at) FROM orders;"
}
# Required: row counts match ± expected delta + app smoke below
curl -sf http://staging-api/health && curl -sf http://staging-api/readyz
```

## 3. Replication Lag Check (Go/No-Go Gate)
```bash
# Postgres replica
psql -h replica.db -c "SELECT now() - pg_last_xact_replay_timestamp() AS lag;"
# MySQL/RDS (CloudWatch): mysql> SHOW SLAVE STATUS\G  # Seconds_Behind_Master
# Kafka MM2: kafka-consumer-groups.sh --describe | awk '{print $NF}'  # LAG column
# Gate: proceed only if lag < RPO (e.g., 900s for 15-min RPO)
```

## 4. Log Snippets
```
# Healthy shipping
LOG: restartpoint complete, replayed 412 WAL segments, lag 1.8s
# Lag breaching RPO
WARN  replica lag 1240s > RPO 900s — HOLD failover, investigate primary load
# Successful promotion
LOG: promoted to primary, timeline 14, accepting writes
# Split-brain attempt (blocked)
FATAL: refusing write — node is demoted primary, read-only fence active
ERROR app: connection refused writing to old primary (expected — fence working)
# Untested restore surprise
FATAL: backup manifest checksum mismatch — base backup corrupt (drill caught it, prod didn't... yet)
```

## 5. Cutover Sequence (Copy-Paste)
```bash
export PRIMARY=primary.db SECONDARY=replica.db TTL_WAIT=120
# 1. Fence writes on old primary
psql -h $PRIMARY -c "ALTER SYSTEM SET default_transaction_read_only=on; SELECT pg_reload_conf();"
# 2. Drain: wait lag < 30s
watch -n5 "psql -h $SECONDARY -t -c \"SELECT extract(epoch from now()-pg_last_xact_replay_timestamp());\""
# 3. Promote
pg_ctl -D /var/lib/postgresql/replica promote  # or: aws rds promote-read-replica --db-instance-identifier prod-replica
# 4. Switch DNS (Route53 failover record, TTL 60)
aws route53 change-resource-record-sets --hosted-zone-id Z123 --change-batch file://failover.json
sleep $TTL_WAIT
# 5. Verify: writes + reads + lag zero
psql -h db.example.com -c "CREATE TABLE IF NOT EXISTS dr_probe(t timestamptz default now()); INSERT INTO dr_probe DEFAULT VALUES RETURNING *;"
curl -sf https://api.example.com/health && curl -sf https://api.example.com/readyz
```

## 6. Alerts
```promql
time() - pgbackrest_last_backup_timestamp > 16*3600          # backup stale
pg_replication_lag_seconds > 900                             # RPO breach
probe_success{region="primary"} == 0 and probe_success{region="secondary"} == 1  # cutover candidate
```

Order: lag gate → fence → promote → DNS → verify → failback plan. Never skip verify.
