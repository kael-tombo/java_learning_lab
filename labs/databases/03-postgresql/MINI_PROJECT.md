# PostgreSQL — Mini Project

## Scenario
A teammate needs a runnable example of PostgreSQL schemas, data types, and transactional DDL habits by end of day, small enough to review in one sitting.

## What you ship
A scripted walkthrough covering the schema layout, typed columns, and atomic DDL, with seed data, ordered steps, and a verification section at the end.

## Working sequence
1. First, frame the tenant schema layout separating shared and private tables, then note the one surprise worth remembering.
2. Next, trace the invoice table with its identity key and numeric totals, and capture the check query beside it.
3. Then, draft the timestamp discipline documenting time-zone storage choices, then explain the result to a reviewer aloud.
4. After that, load the single-transaction DDL script adding two related tables, and file the script where the next step finds it.
5. Further, run the search-path experiment showing schema resolution order, while keeping every statement re-runnable.
6. Finally, shape the default-value and nullability audit of every column, and record what changes in the output.

## Reference snippet
```sql
SELECT id FROM tenants
WHERE id IS NOT NULL
ORDER BY id
FETCH FIRST 10 ROWS ONLY;
```

## Verification
- Rerun the full sequence twice; the second pass must stay green.
- Show how schemas namespace tables so tenants and shared objects stay separated, and point to the line where that shows up in the results.
- Demonstrate that PostgreSQL column types here include serial-style identity, text, numeric, and timestamps, backed by one concrete observation.
- Keep the invoices row counts consistent across every rerun.

## Concept tie-in
This drill exercises the habits end to end: transactional DDL lets several schema changes commit or roll back atomically.

## Setup checklist
- A scratch schema is set aside for this work, away from shared databases.
- Seed rows for tenants and invoices loaded and counted.
- Surprises worth quoting get jotted in an open notes file.
- The first edit waits until the rollback or re-seed path is confirmed.

## Next step
Carry these scripts into the real-world project as the starting scaffold.

## Hand-off
- The finished scripts folder gets tagged so the next lab skips re-reading every file.
- Surprises survive the handoff because the notes file goes to whoever reruns the exercises.
- A peer reruns every script without edits before this checklist is marked done.

