# Lab 03: Interactive Reports — Real World Project

## Scenario
A healthcare provider's claims operations team works an Interactive Report of
120,000 claims. Users need to filter by date range, provider, payer, and status;
drill from a claim to its service lines; export filtered results to CSV for
downstream analysis; and receive a scheduled daily summary they do not have to
log in to see. Today the report is a single unfiltered query against a
120,000-row table with export enabled for every user, taking 9 seconds to load
and occasionally timing out at month-end when the volume triples.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX documentation)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/

## Architecture
```
Claims IR (paged, never unbounded)
   │
   ├─ Filter page items (date range, provider, payer, status)
   │     └─ ALL bound into the query — no post-filtering
   │
   ├─ Aggregations: SUM(allowed), COUNT, AVG(days in AR) in-query
   │
   ├─ Drill: Claim → Service lines (context passed via items)
   │
   ├─ CSV export: enabled for authorised roles only
   │              disabled on PHI-bearing regions
   │
   └─ Scheduled email: daily summary to ops distribution list

Indexes: (claim_date), (provider_id), (payer_id), (status)
```

## Implementation sketch
```sql
-- Index-friendly range predicate, not TRUNC(column)
SELECT c.claim_id, c.claim_number, p.provider_name, c.service_date,
       c.status, c.allowed_amount, c.paid_amount
  FROM claims c
  JOIN provider p ON p.provider_id = c.provider_id
 WHERE c.service_date >= :P1_START_DATE          -- range, sargable
   AND c.service_date <  :P1_END_DATE + 1
   AND (:P1_PROVIDER_ID IS NULL OR c.provider_id = :P1_PROVIDER_ID)
   AND (:P1_STATUS      IS NULL OR c.status      = :P1_STATUS)
   AND (:P1_SEARCH     IS NULL
        OR UPPER(p.provider_name) LIKE '%' || UPPER(:P1_SEARCH) || '%')
 ORDER BY c.service_date DESC;
```

## Requirements
- F1: Parameterised query with all filters bound into the SQL.
- F2: Dynamic date range using a sargable range predicate.
- F3: Provider, payer, and status filters with cascading dependencies.
- F4: Aggregations computed in-query: count, SUM(allowed), AVG days in AR.
- F5: Two-level drill: claim → service lines, with context preserved.
- F6: CSV export restricted by authorisation, disabled on PHI regions.
- F7: Scheduled daily summary email to an ops distribution list.
- F8: Index strategy supporting the filter combinations actually used.
- F9: Row-level security so users see only their assigned payers.
- F10: Load test at month-end volume (360,000 claims).
- NF1: Report loads under 2 seconds p95 at peak volume.
- NF2: Filter response under 1 second.
- NF3: CSV export of 100,000 rows under 30 seconds.
- NF4: Security baseline — no unauthorised PHI export path.
- NF5: Month-end volume loadable without timeout.
- NF6: Documented rollback for every region and filter change.

## Milestones
- Week 1: Baseline — load time, filter latency, export timing at peak volume.
- Week 2: Filters bound into SQL; sargable date predicate implemented.
- Week 3: Aggregations and computed columns moved into the query.
- Week 4: Drill-down built; context preservation verified.
- Week 5: Export authorisation and scheduled email delivery.
- Week 6: Index tuning and load test at 360,000 rows.

## Verification
- EXPLAIN PLAN confirms index usage for each filter combination.
- Load test at month-end volume with 50 concurrent users.
- Fault injection: filter combination with no results; invalid date range.
- Security test: unauthorised user attempts CSV export of PHI.
- Timing comparison before and after with identical data volume.

## Rollback
Region configuration changes are reversible in the builder; export settings are
configuration; index additions are removable. Document rollback steps for every
change.