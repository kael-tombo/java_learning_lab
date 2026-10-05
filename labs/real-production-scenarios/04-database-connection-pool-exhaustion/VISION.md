# VISION — On-Call Excellence for Pool Exhaustion

## 1. Future State
Pool saturation pages with the culprit attached: leak stack or slow-query digest. Dashboards show active/idle/pending per pod beside DB load, and no deploy can oversubscribe the database because sizing is checked in CI.

## 2. What Good Looks Like
- `leakDetectionThreshold` always on in prod with sampled stacks.
- Pending-thread alert fires before users feel the cliff.
- Fleet sizing math lives beside the DB `max_connections` dashboard.

## 3. Behaviors
Check app-side before blaming DB, kill blockers surgically, fix close-discipline not pool size first.

## 4. Anti-Vision
Blind pool bumps crushing Postgres, restarts without leak stacks, holding transactions across HTTP calls.

## 5. Commitment
This week: enable leak detection + pending alert on one service. Next: publish fleet-vs-DB budget and add PgBouncer evaluation.

> Excellence = every checkout returns its connection; every pool fits its database.
