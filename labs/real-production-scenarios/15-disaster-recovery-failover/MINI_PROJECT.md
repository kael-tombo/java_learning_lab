# Lab 15 — Mini Project: Reproduce + Detect + Fix Failover

## Objective
Simulate primary/replica Postgres with Docker, break primary, cut over — ~60 minutes + cleanup.

## Part 1 — Reproduce (20 min)
1. `docker run -d --name pg-primary -e POSTGRES_PASSWORD=p postgres:16`; create `app` DB + `orders` table + seed 1000 rows.
2. `pg_basebackup` to build `pg-replica` (or simulate with a second container + periodic `pg_dump` restore).
3. Write `lag.sh` reporting row-count delta + `max(updated_at)` gap (your RPO proxy).
4. Kill primary (`docker stop pg-primary`); show app errors (reproduce outage).

## Part 2 — Detect (20 min)
1. Health script `region_health.sh`: primary probe red, replica probe green.
2. Backup-age check: `stat` dump timestamp; alert if > your toy RPO (15 min).
3. Decision memo: lag 45s (<RPO) + replica verified → FAIL OVER; or lag 30 min (>RPO) → HOLD. Write both branches.
4. DNS simulation: `/etc/hosts`-style switch file pointing `db.local` to replica IP.

## Part 3 — Fix (20 min)
1. Promote replica (restart as writable); fence old primary (keep stopped + note read-only intent).
2. Flip `db.local` to replica; run app smoke (insert + select + count match).
3. Time every phase; total vs your 30-min toy RTO.
4. Failback: re-sync (dump/restore), flip back, verify zero dupes; document runbook.

## Deliverables
- `lag.sh`, `region_health.sh`, timed phase log, decision memo, cutover runbook.
- Success: outage reproduced, lag-gated decision documented, cutover verified with data check.

## Grading
- Reproduce (30%), Detect/decision (35%), Fix + failback + timing (35%).
