# EBS Architecture — Real World Project

## Scenario
A retail chain runs EBS R12.2 across 12 stores and a central distribution centre:
2,800 named users, 400 store terminals, and a 4.5 TB database. The current
architecture has no documented map, three undocumented custom packages touching
core tables, and a concurrent manager that periodically stalls the whole
instance. Your first deliverable is an architecture that the next administrator
can actually operate — and that reveals where the risk lives.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/
- (link removed) (EBS architecture and deployment)
- (link removed) (EBS installation guide)

## Architecture
```
Store terminals / Corporate users
            │
      Desktop tier (Forms client, browser)
            │
   ┌────────▼─────────────────────────────────┐
   │ Application tier (shared APPL_TOP on NFS)│
   │ OHS ─ Forms server ─ OAF ─ Admin         │
   │ Concurrent Manager (specialized queues)  │
   └────────┬─────────────────────────────────┘
            │  public APIs only
   ┌────────▼─────────────────────────────────┐
   │ Database tier (Oracle DB 19c)            │
   │ core tables ─ API layer ─ SLA            │
   │ edition-based redefinition enabled       │
   └──────────────────────────────────────────┘
```

## Implementation sketch
```sql
-- Public API boundary: never write to core tables directly
DECLARE
  x_return_status VARCHAR2(2);
BEGIN
  DBMS_OUTPUT.PUT_LINE(x_return_status); -- placeholder for API call
  -- Real pattern:
  -- PO_REQ_CREATE_PUB.CREATE_PURCHASE_ORDER(...)
  --   returns x_return_status, p_error_code
END;
/
-- Confirm which custom code bypasses the API layer
SELECT owner, name, type FROM all_source
 WHERE UPPER(text) LIKE '%UPDATE_GL_%' OR UPPER(text) LIKE '%INSERT INTO GL_%'
   AND owner NOT IN ('AP','AR','FA','GL');
```

## Requirements
- F1: Full architecture map covering all tiers, components, and file roots.
- F2: Customisation inventory identifying every object bypassing public APIs.
- F3: Request traces for the three most business-critical transactions.
- F4: Multi-node cluster design with service specialisation per node.
- F5: Concurrent processing model with per-queue capacity and monitoring.
- F6: EBR strategy so upgrades never require patching production objects.
- F7: Component version inventory with upgrade-blocking incompatibilities listed.
- F8: Failure-domain analysis — what breaks what when a tier is lost.
- F9: Onboarding document for a new EBS administrator.
- F10: Remediation plan for the three undocumented custom packages.
- NF1: Architecture map covers 100% of running services.
- NF2: Custom code bypassing APIs reduced to zero or formally accepted.
- NF3: Concurrent manager stalls eliminated with per-queue monitoring.
- NF4: Security baseline — segmented tiers, TLS, least-privilege DB accounts.
- NF5: RPO/RTO per tier with a documented restore drill.
- NF6: Documented rollback for every architecture change.

## Milestones
- Week 1: Discovery — service inventory, node roles, custom code scan.
- Week 2: Architecture map drafted and reviewed with the operations team.
- Week 3: CM redesign with specialisation and per-queue monitoring.
- Week 4: Custom code remediation or formal exception for each package.
- Week 5: EBR enablement plan and first edition-based change.
- Week 6: Onboarding documentation and knowledge transfer complete.

## Verification
- Trace validation — each documented trace replayed against a live instance.
- Load test confirming the redesigned CM absorbs peak load.
- EBR rehearsal: run a change against the edition, prove rollback is trivial.
- Restore drill for the database tier with a verified recovery point.

## Rollback
Architecture documentation is versioned; CM changes are reversible by queue
disable; EBR savepoints allow abandoning an edition without data loss.
Document rollback steps for every change.