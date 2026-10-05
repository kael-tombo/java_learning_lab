# VISION — On-Call Excellence for Slow Queries & Deadlocks

## 1. Future State
No slow query ambushes deploys. Every digest has an SLO, plan regressions alert before users notice, and DB deadlocks are retried invisibly with idempotency — paged only when ordering discipline breaks.

## 2. What Good Looks Like
- `pg_stat_statements` top-10 reviewed weekly; auto_explain captures slow plans.
- Deploys with migration/ORM changes trigger automatic EXPLAIN diff on staging.
- Retry-with-backoff + idempotency is the default template, not copy-paste heroics.

## 3. Behaviors
Prove DB-bound with traces before scaling apps, kill blockers surgically, fix order not timeouts first.

## 4. Anti-Vision
More pods for a missing index, instant retries amplifying collisions, peak-hour DDL locking checkout.

## 5. Commitment
This week: enable `log_lock_waits` + digest SLO on one DB. Next: add ordered-update rule + retry template to your service scaffold.

> Excellence = fast plans, short ordered txns, retries users never feel.
