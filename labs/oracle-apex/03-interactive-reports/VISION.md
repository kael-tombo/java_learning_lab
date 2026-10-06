# Lab 03: Interactive Reports — Vision

## Where this lab takes you
From a working Interactive Report to one that filters dynamically, drills down,
exports safely, and stays fast as the data grows.

## The Arc
1. **Anatomy** — what an IR is and what it does without configuration.
2. **Filters** — dynamic date range and search using bind variables.
3. **Master-detail** — navigation that keeps context.
4. **Aggregation** — rollups without extra regions.
5. **Export** — CSV download, and the cases where it must be controlled.
6. **Email delivery** — bursting a report to someone who is not logged in.
7. **Performance** — keeping an IR usable at millions of rows.

## Milestones (checkable)
- [ ] M1: Build an IR and identify its region, query, and column defaults.
- [ ] M2: Add dynamic date-range and search filters using bind variables.
- [ ] M3: Implement master-detail navigation that preserves the filter context.
- [ ] M4: Add aggregations and a computed column.
- [ ] M5: Configure CSV download and disable it deliberately where it is unsafe.
- [ ] M6: Set up email delivery to a distribution list.
- [ ] M7: Explain why a large IR must not select from a 5M-row table unbounded.
- [ ] M8: Measure before/after for the filtering pattern.

## Anti-Goals
- Filtering in the report query without bind variables.
- Leaving CSV download enabled on a report whose data a user may not export.
- Building a separate region for every aggregate the report could do itself.
- Assuming IR pagination means the query is cheap.

## The one-sentence thesis
An Interactive Report is a query with a UI — the filtering must reach the
database, and pagination is a display concern that does not make the query
safe.