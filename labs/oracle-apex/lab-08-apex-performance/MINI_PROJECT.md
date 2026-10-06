# Lab 08: APEX Performance — Mini Project

## Goal
Take a deliberately slow dashboard page from 12 seconds to under 3 seconds, with
a measured before and after — in 90 minutes.

## Requirements
- R1: An APEX Debug timing breakdown captured before any change.
- R2: A component attribution table naming the largest contributors.
- R3: The single largest contributor identified and fixed first.
- R4: An index added or verified for the dominant query.
- R5: One region removed or made lazy with the saving measured.
- R6: Session state audited with unnecessary content removed.
- R7: A cache applied to the most expensive stable region.
- R8: A before/after timing table with the same data volume.

## Steps

1. Create the slow page with 8 reports and 3 charts over large tables.
2. Run APEX Debug and record the breakdown by component.
3. Build the attribution table and rank the contributors.
4. Fix the largest contributor — usually an unindexed or unbound query.
5. Add or verify the index; re-measure.
6. Remove or lazy-load one region; re-measure.
7. Dump session state; remove anything not needed across pages.
8. Apply a cache to the most expensive stable region; re-measure.
9. Produce the final before/after table.

## Acceptance criteria
- The Debug breakdown is captured before any modification.
- Each fix is measured independently, not bundled.
- The final timing is under 3 seconds on the same data volume.
- Session state contains only cross-page-required items.
- The cache has a documented invalidation trigger.

## Stretch
- Identify a query using a literal instead of a bind variable.
- Compare the effect of removing one chart region versus one report region.