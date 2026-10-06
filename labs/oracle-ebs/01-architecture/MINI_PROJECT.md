# Lab 01: EBS Multi-Tier Architecture — Mini Project

## Goal
Design and document a complete high-availability EBS R12.2 topology for 5,000
concurrent users across US / EMEA / APAC, in 90 minutes.

## Requirements
- R1: Three application-tier nodes, each with an explicit service inventory
      (OHS, Forms process count, OAF thread count, CM queues, Admin state).
- R2: Forms processes sized at 1 per 50 users, OAF threads at 1 per 100 users,
      distributed by regional user share.
- R3: F5 BIG-IP pool definitions for `ebs_forms_pool`, `ebs_oaf_pool`, and
      `ebs_cm_pool` with the correct load method, persistence, and monitor.
- R4: Two RAC services — ONLINE (service-time goal) and BATCH (throughput goal)
      — created via `DBMS_SERVICE`, with failover settings justified.
- R5: Data Guard SYNC transport with Fast-Start Failover targeting RPO < 5 min,
      RTO < 30 min.
- R6: Specialized Concurrent Managers (report / interface / batch) each pinned
      to a target node.
- R7: Work shifts defined in DB time zone for the three regional peaks.
- R8: Four monitoring queries plus documented alert thresholds.

## Steps
1. Split the 5,000 users into US 2,500 / EMEA 1,500 / APAC 1,000 and record the
   basis for the split.
2. Compute per-node Forms processes and OAF threads; sanity-check the totals.
3. Write the three `tmsh` pool definitions; verify each persistence matches the
   statefulness of its traffic type.
4. Create the two RAC services and note which goal suits long-running batch.
5. Configure Data Guard SYNC + FSFO and state the resulting RPO/RTO.
6. Create the three specialized queues with `FND_CONCURRENT_QUEUE_PUB`.
7. Convert the regional peaks into DB-time shifts (EMEA and APAC need care).
8. Write the monitoring queries and set thresholds for each metric.
9. Draft the `adop` rolling cutover plan, including `phase=abort` rollback.
10. Review the whole document against R1–R8 before submitting.

## Acceptance criteria
- Every node's service inventory is explicit — no "same as node 1".
- The health check on `ebs_forms_pool` is application-level, not TCP-only.
- ONLINE and BATCH services use different goals and different CLB goals.
- Work shifts are stated in DB time zone, not local time.
- The cutover plan names a rollback action for each phase.

## Stretch
- Add a capacity model for 20% year-on-year user growth and name the node-add
  trigger threshold.
- Design the failover rehearsal runbook and record the RTO you would measure.