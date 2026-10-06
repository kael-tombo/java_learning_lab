# Lab 02: Workshop Builder — Real World Project

## Scenario
A logistics company's dispatch console has 40 dispatchers working an Operations
screen with an Interactive Report of 2,000 open shipments. Selecting a shipment
currently submits the whole page to show its lines, leg history, and assigned
driver — three regions that make up the dispatcher's entire working view. Each
selection costs a full page render of 1.8 seconds, so a dispatcher investigating
one problem costs over 20 seconds of waiting. They have started opening shipments
in a second browser tab to avoid the wait, which has made it impossible to see
the shipment and its context together.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX documentation)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
Operations page (no full page submit)
   │
   ├─ Master: Interactive Report — 2,000 open shipments
   │     └─ row selection → :P_SHIPMENT_ID (hidden item)
   │
   └─ Dynamic Action: "Selection" on master → Refresh (AJAX)
              │
              ├─► Detail 1: Shipment lines (Interactive Grid)
              ├─► Detail 2: Leg history (Interactive Report)
              └─► Detail 3: Assigned driver and vehicle (Form region)

State: :P_SHIPMENT_ID in session state — survives page navigation
Fallback: 2,000-row master is paged, never loaded wholesale
```

## Implementation sketch
```sql
-- Detail regions read the shared selection item, never a literal
SELECT line_id, leg_seq, origin, destination, status, eta
  FROM shipment_leg l
 WHERE l.shipment_id = :P_SHIPMENT_ID     -- shared state, not a page submit
 ORDER BY l.leg_seq;
```

```javascript
// Dynamic Action configuration (no JavaScript required)
// Event:   Selection (Interactive Report region)
// Action:  Refresh
// Target:  Detail regions 1, 2, 3
// When:    "after refresh", page items P_SHIPMENT_ID is not null
```

## Requirements
- F1: Master region with single-row selection and no page submission.
- F2: Selection held in a session-state item shared by all detail regions.
- F3: All three detail regions refresh from one selection via AJAX.
- F4: Readable empty state before the first selection.
- F5: Graceful handling of invalid or deleted selections.
- F6: Second-level master-detail (leg → leg transaction).
- F7: Selection restored when returning from a detail drill-down.
- F8: Filtering and search preserved in the master without losing selection.
- F9: Dispatcher keyboard shortcuts for next/previous shipment.
- F10: Latency and error-rate monitoring.
- NF1: Selection-to-detail latency under 300 ms (from 1.8 s).
- NF2: Zero lost context for a dispatcher working one shipment.
- NF3: p95 page load under 3 s.
- NF4: Security baseline — dispatcher sees only assigned shipments via row security.
- NF5: No functional regression in filtering, search, or export.
- NF6: Documented rollback — pattern is additive over the existing page.

## Milestones
- Week 1: Baseline — measure current selection latency and dispatcher workflow.
- Week 2: Master region and shared state item implemented.
- Week 3: Detail regions converted to AJAX refresh.
- Week 4: Empty state, invalid selection handling, second-level master-detail.
- Week 5: Keyboard shortcuts and selection restoration.
- Week 6: Pilot with 5 dispatchers; measure and adjust.

## Verification
- APEX Debug confirms no full page submit on selection.
- Fault injection: delete a shipment mid-session; confirm a clear message.
- Keyboard-only workflow test with a dispatcher.
- Latency measured before and after with the same data set.
- Confirm dispatcher row security still applies to the master.

## Rollback
The change is confined to Dynamic Actions and region configuration on an existing
page; removing the Dynamic Action restores the submitting behaviour.
Document rollback steps for every change.