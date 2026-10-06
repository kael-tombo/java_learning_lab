# Lab 03: APEX SQL Workshop — Mini Project

## Goal
Use SQL Workshop end to end — create objects, load data, query, and save
scripts — in 90 minutes.

## Requirements
- R1: A schema object inventory produced from the Object Browser.
- R2: Three tables created: one via the browser, two via DDL script.
- R3: Constraints added and the effect on inserts demonstrated.
- R4: A two-table join built in the Query Builder and rewritten as SQL.
- R5: A 500-row CSV loaded through the Data Workshop with column mapping.
- R6: A saved script with bind variables re-run at different values.
- R7: A written list of SQL Workshop limits and the tool for each.

## Steps
1. Open the Object Browser and inventory the existing schema.
2. Create a table through the browser; note the generated DDL.
3. Create two tables through a DDL script including constraints and indexes.
4. Attempt an insert violating each constraint; record the errors.
5. Build a two-table join in the Query Builder; export the SQL.
6. Load a 500-row CSV via the Data Workshop, mapping columns.
7. Validate the load with row counts and a checksum.
8. Save a script with two bind variables; run it at three value sets.
9. Write the limits list.

## Acceptance criteria
- All three tables created and constraints verified by violation.
- Query Builder SQL matches the hand-written version in result and plan.
- CSV load produces the expected row count with no silent truncation.
- Script runs three times with different bind values.
- Limits list names the correct tool for each limitation.

## Stretch
- Compare the Query Builder's SQL with an optimised equivalent.
- Demonstrate a case where the browser path is wrong for production.