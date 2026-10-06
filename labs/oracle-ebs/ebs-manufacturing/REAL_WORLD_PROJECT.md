# EBS Manufacturing — Real World Project

## Scenario
A medical device manufacturer produces 4,200 SKUs across two plants with full
lot genealogy required by regulators. On-time delivery is 78%, expedited freight
costs $1.4M/year, and no one can answer "which finished lots used the recalled
raw lot R-2025-114" without a two-day manual trace. Scheduling is done in a
spreadsheet that has never agreed with the system. You own the fix.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/sc/24b/ocins/ (Supply Chain)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS Manufacturing)
- https://docs.oracle.com/database/121/MNBRA/ (Manufacturing concepts)

## Architecture
```
Item master ─► BOM (multi-level, eff-dated) ─► Routing ─► Work centres
      │                                              │
      └──────────► ECO / ECN (revision control)       ▼
                                          MPS ─► MRP ─► CRP capacity check
                                                       │
                                                       ▼
                                    WIP job ─► issue / backflush ─► complete
                                                       │
                                    Lot genealogy ◄─────┴── Quality results
                                          │
                                          ▼
                              Recall trace + compliance reporting
```

## Implementation sketch
```sql
-- Forward genealogy: which finished lots used this raw lot?
SELECT g.object_type, g.from_number, g.to_number, g.plan_qty
  FROM mtl_object_genealogy g
 WHERE g.from_type = 13  -- lot
   AND g.from_number = 'R-2025-114'
   AND g.object_type IN (5, 11)  -- WIP, FG
 ORDER BY g.object_type;

-- Work-centre load versus capacity
SELECT wi.resource_code, wi.operation_seq,
       SUM(wr.process_quantity * wi.run_time) AS load_hrs,
       (SELECT SUM(available_hrs) FROM crp_resource_HARS
         WHERE resource_code = wi.resource_code) AS capacity_hrs
  FROM wip_operations wo
  JOIN WIP_OPERATION_RESOURCE wi ON wi.operation_id = wo.operation_id
  JOIN WIP_OPERATIONS wr ON wr.wip_operation_id = wi.wip_operation_id
 GROUP BY wi.resource_code, wi.operation_seq
HAVING SUM(wr.process_quantity * wi.run_time) >
       (SELECT SUM(available_hrs) FROM crp_resource_HARS
         WHERE resource_code = wi.resource_code);
```

## Requirements
- F1: Effective-dated BOM and routing governance with ECO/ECN workflow.
- F2: Full lot genealogy, forward and backward, answering a recall query in
      under 5 minutes.
- F3: MPS/MRP/CRP integration replacing the spreadsheet schedule.
- F4: Work-centre capacity model reflecting the real bottleneck.
- F5: Backflush and yield accounting for repetitive and flow lines.
- F6: Quality integration: results, defects, and their genealogy impact.
- F7: Expedite analysis identifying true constraint-driven expedites.
- F8: Compliance reporting for regulators on lot and genealogy data.
- F9: Shop-floor data collection design (scanner/terminal ready).
- F10: Schedule performance dashboard: OTD, cycle time, expedite spend.
- NF1: On-time delivery at or above 95%.
- NF2: Recall impact query answered in under 5 minutes.
- NF3: Expedite freight reduced by at least 50%.
- NF4: Security baseline — genealogy and cost data access restricted.
- NF5: RPO/RTO for the manufacturing database with a restore drill.
- NF6: Documented rollback for every routing, BOM, and planning change.

## Milestones
- Week 1: Baseline — OTD, expedite spend, genealogy trace timing, data quality.
- Week 2: BOM and routing data cleansed and validated with operations.
- Week 3: ECO/ECN workflow live with effective-dated revision control.
- Week 4: MPS/MRP/CRP planning integrated and generating the schedule.
- Week 5: Genealogy and compliance reporting built and verified.
- Week 6: Shop-floor collection pilot and dashboard go-live.

## Verification
- Recall drill: inject a synthetic lot recall and time the full trace.
- Backtest planning against 6 months of actuals; measure plan stability.
- Fault injection: routing gap, work-centre overload, missing lot link.
- Restore drill verifying genealogy and effective-dated structures survive.

## Rollback
BOM and routing revisions are effective-dated and reinstatable; planning rules
are configuration; genealogy is append-only by design and never rolled back.
Document rollback steps for every manufacturing change.