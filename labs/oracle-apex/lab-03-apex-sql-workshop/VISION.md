# Lab 03: APEX SQL Workshop — Vision

## Where this lab takes you
From using SQL Workshop as a convenience to understanding it as database
administration: the Object Browser, query tooling, DDL execution, and where its
limits are.

## The Arc
1. **What it is** — a browser-based database tool inside APEX.
2. **Object Browser** — browse, create, alter, drop.
3. **SQL Commands** — run DDL and DML with result inspection.
4. **Query Builder** — visual construction for simple joins.
5. **Data Workshop** — loading external CSV data.
6. **Scripts** — saving and re-running reusable SQL.
7. **RESTful Services** — the bridge from SQL Workshop to ORDS.
8. **Limits** — what it cannot do, and what to use instead.

## Milestones (checkable)
- [ ] M1: Explain where SQL Workshop sits relative to the database.
- [ ] M2: Browse the schema and create a table through the Object Browser.
- [ ] M3: Write and run DDL, then alter and drop the object.
- [ ] M4: Use the Query Builder for a two-table join and compare with SQL.
- [ ] M5: Load a CSV through the Data Workshop with column mapping.
- [ ] M6: Save a script and re-run it with different bind values.
- [ ] M7: State the limits and name the tool to use for each.

## Anti-Goals
- Treating SQL Workshop as a production deployment tool.
- Running DDL in a schema you do not own.
- Using the Query Builder for anything beyond a simple join.
- Believing a browser session is an appropriate place for long transactions.

## The one-sentence thesis
SQL Workshop is a convenience for development and exploration — production
changes belong in version-controlled scripts applied through a controlled process.