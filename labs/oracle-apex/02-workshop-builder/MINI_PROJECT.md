# Lab 02: Workshop Builder — Mini Project

## Goal
Build a master-detail page where selecting a row refreshes a detail region via
AJAX, in 90 minutes.

## Requirements
- R1: A master region (Interactive Report) with a single-row selection.
- R2: A hidden page item holding the selected ID, set from the selection.
- R3: A detail Interactive Grid filtered by that page item.
- R4: A Dynamic Action: on row selection, refresh the detail region.
- R5: A readable empty state before any selection is made.
- R6: Graceful handling of an invalid or stale selection.
- R7: A second detail region driven by the same selection.
- R8: Latency comparison against a submitting (non-AJAX) version.

## Steps
1. Load sample data for orders and order lines.
2. Create the page with a master Interactive Report.
3. Enable row selection and map it to a hidden page item.
4. Create the detail Interactive Grid with the item as a filter.
5. Add the Dynamic Action on selection to refresh the detail region.
6. Verify with APEX Debug that no full page submit occurs.
7. Confirm the empty state renders before any selection.
8. Add a second detail region and confirm both refresh.
9. Force an invalid selection and confirm a clear message.

## Acceptance criteria
- Selecting a row updates detail without a page submission.
- The detail region is empty and readable before the first selection.
- Two detail regions refresh from the same selection.
- An invalid selection produces a clear message, not a SQL error.
- The latency comparison shows a measurable improvement.

## Stretch
- Add a master-detail on a second level (line → transaction).
- Persist the selection in session state so a page return restores it.