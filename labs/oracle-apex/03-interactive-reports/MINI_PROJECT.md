# Lab 03: Interactive Reports — Mini Project

## Goal
Build a production-shaped Interactive Report with dynamic filtering, aggregation,
master-detail navigation, export controls, and email delivery in 90 minutes.

## Requirements
- R1: An IR region with a parameterised query using bind variables.
- R2: Dynamic date-range filter using page items.
- R3: A search filter with a `%` bind variable and an index-friendly predicate.
- R4: Column aggregations and one computed column.
- R5: Master-detail navigation preserving the current filter context.
- R6: CSV download enabled, plus a deliberate disable on a sensitive region.
- R7: Email delivery of the report to a distribution list.
- R8: A performance check demonstrating the filtered query versus the unfiltered.

## Steps
1. Load 100,000 rows of transactional data across a date range.
2. Create the IR and write its parameterised query.
3. Add a date-range page item pair and bind both into the query.
4. Add a search item and apply it to an indexed column.
5. Configure aggregations on numeric columns and add a computed column.
6. Build the detail page and pass the context through items.
7. Configure CSV download on the main region; disable it on the sensitive region.
8. Set up scheduled email delivery.
9. Compare EXPLAIN PLAN and timing for the filtered and unfiltered queries.

## Acceptance criteria
- No filter is applied by post-processing rows the database already returned.
- The date filter uses a range predicate that can use an index.
- Aggregations compute in the query, not in report post-processing.
- Master-detail navigation preserves the date range.
- CSV download is disabled on the region containing restricted data.
- The filtered query plan differs measurably from the unfiltered one.

## Stretch
- Add a second-level drill and pass three levels of context.
- Demonstrate CSV export of 100,000 rows and measure the time.