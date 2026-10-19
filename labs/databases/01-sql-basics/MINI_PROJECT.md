# SQL Basics — Mini Project

## Scenario
A teammate needs a runnable core SELECT example — filtering, sorting, and paging — by end of day, small enough to review in one sitting.

## What you ship
A scripted walkthrough with seed data, ordered steps, and a verification section at the end.

## Working sequence
1. First, shape the member roster filtered by status and city, and file the script where the next step finds it.
2. Next, assemble the loan list sorted by due date descending, while keeping every statement re-runnable.
3. Then, compose the paged directory query using OFFSET plus FETCH FIRST, and record what changes in the output.
4. After that, frame the NULL-safe status filter using IS NULL, then note the one surprise worth remembering.
5. Further, trace the aliased column list that renames cryptic columns, and capture the check query beside it.
6. Finally, draft the pattern search with LIKE and a documented wildcard, then explain the result to a reviewer aloud.

## Reference snippet
```sql
SELECT id FROM members
WHERE id IS NOT NULL
ORDER BY id
FETCH FIRST 10 ROWS ONLY;
```

## Verification
- Rerun the full sequence twice; the second pass must stay green.
- Show that WHERE filters rows before any grouping or ordering takes place, and point to the line where that shows up in the results.
- Demonstrate that ORDER BY controls presentation order and accepts several sort keys, backed by one concrete observation.
- Keep the loans row counts consistent across every rerun.

## Concept tie-in
This drill exercises the fundamentals end to end: FETCH FIRST limits returned rows in standard SQL without proprietary clauses.

## Setup checklist
- Shared databases stay untouched because a scratch schema is reserved here.
- Seed rows for members and loans loaded and counted.
- Keep a notes file open; quote-worthy surprises land there.
- Confirm the rollback or re-seed path before the first edit.

## Next step
Carry these scripts into the real-world project as the starting scaffold.

## Hand-off
- The next lab inherits a tagged scripts folder instead of re-reading every file.
- The notes file goes to whoever reruns the exercises, and the surprises survive the handoff that way.
- Checklist completion waits for a peer rerun of every script, unedited.

