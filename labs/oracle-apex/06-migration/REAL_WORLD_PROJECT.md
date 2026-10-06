# Lab 06: APEX Migration — Real World Project

## Scenario
An industrial distributor runs its entire inventory operation on Oracle Forms —
23 canvases, 57 data blocks, 340 triggers, 48 LOVs. Users report the application
is slow, support tickets are unresolvable because nobody understands the logic,
and the Forms deployment client has become expensive. The business wants to move
to APEX. The programme has been estimated by a manager at "roughly 23 screens, so
about three months", and the project office has accepted that figure.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX documentation)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/lnpls/

## Architecture
```
FORMS (current)                      APEX (target)
  23 canvases                          23 pages
  57 data blocks                       Forms + Interactive Reports
  340 triggers                         165 deleted · 175 converted
  48 LOVs                              Popup LOVs + dynamic actions
  118 POST-QUERY  ─────deleted────►   Absorbed into region SQL joins
   47 KEY-QUERY   ─────deleted────►   No equivalent needed
   Client-tier logic  ────moved────►  Server-side processes and Dynamic Actions
   Level-3 constraints ──kept──────►  Identical database enforcement
   31% of objects    ────dropped───►  Redundant or simplified
```

## Implementation sketch
```sql
-- POST-QUERY deleted: the join does the work once instead of per record
-- Forms ONTBL.POST-QUERY ran per record as the user navigated:
SELECT o.stock_id, i.description AS item_description, i.uom,
       l.location_name, o.quantity_on_hand
  FROM ontbl o
  JOIN items     i ON i.item_id     = o.item_id
  JOIN locations l ON l.location_id = o.location_id
 WHERE (:P1_ITEM_ID IS NULL OR o.item_id = :P1_ITEM_ID);
-- 1 query for 50 records, versus 50 queries in Forms
```

```sql
-- Classification table: the artefact that changed the estimate
SELECT migration_class,
       COUNT(*) objects,
       ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) pct
  FROM forms_apex_map
 GROUP BY migration_class;
-- 1TO1 35% · SIMPLIFIED 16% · REDUNDANT 37% · NEW 12%
```

## Requirements
- F1: Complete inventory produced by querying Forms source, not interviews.
- F2: Every object classified as 1:1, simplified, redundant, or new.
- F3: Migration estimate corrected from the screen-count basis (~4.6×).
- F4: All POST-QUERY and KEY-QUERY triggers deleted where region SQL absorbs them.
- F5: Client-tier business logic relocated server-side.
- F6: Level-3 database constraint coverage identical before and after.
- F7: Level-2 validation converted to APEX validations with improved messages.
- F8: Return-value LOVs handled with Dynamic Actions.
- F9: Navigation redesigned from user workflow, not the Forms menu tree.
- F10: Staged delivery: read-only pages before core CRUD.
- F11: Parallel-run comparison harness with discrepancy reporting.
- F12: Cutover gate defined on stop-the-line discrepancies, not all of them.
- NF1: Migration completed within the corrected estimate plus contingency.
- NF2: Zero stop-the-line discrepancies in the parallel run.
- NF3: Level-3 constraint enforcement unchanged.
- NF4: Business capability preserved or simplified, never silently lost.
- NF5: Security baseline — APEX row scoping applied to every migrated region.
- NF6: Documented rollback — Forms remains available until cutover sign-off.

## Milestones
- Weeks 1–3: Inventory from source; classification with user confirmation.
- Weeks 4–6: Data model validation; read-only reports and lookups.
- Weeks 7–14: Core CRUD pages from the 57 blocks.
- Weeks 15–18: Complex transactions, savepoint canvases, return-value LOVs.
- Weeks 19–20: Parallel run, discrepancy resolution, cutover.

## Verification
- Inventory reconciled against the Forms source; counts match.
- Spot-check 40 migrated objects against the classification.
- Confirm constraint coverage before and after by querying the data dictionary.
- Parallel run over two weeks; classify every discrepancy.
- Security test: row scoping applied to every migrated region.
- User acceptance testing with real inventory staff before cutover.

## Rollback
Forms remains the system of record until cutover sign-off; each APEX page is
independently reversible by removing it from the menu; no Forms source is modified
during the migration, so the legacy application remains a working fallback.
Document rollback steps for every change.