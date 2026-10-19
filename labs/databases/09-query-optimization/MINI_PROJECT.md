# Query Optimization A — Mini Project

## Brief
Six focused exercises on B-tree index choice and sargable predicate design in the orders domain, each ending with a visible artifact and a one-line explanation.

## Setup
Prepare seed rows for orders and order_lines, sized so the plan output fits on one screen.

## Exercises
1. Exercise on order lookup index on customer id plus order date: run it, then explain the result to a reviewer aloud.
2. Exercise on sargability rewrite removing a function around order date: shape it and file the script where the next step finds it.
3. Exercise on covering-index sketch for the open-orders list: assemble it while keeping every statement re-runnable.
4. Exercise on selectivity comparison between status and primary-key filters: compose it and record what changes in the output.
5. Exercise on plan reading noting seek versus scan on one query: frame it, then note the one surprise worth remembering.
6. Exercise on write-cost note counting index maintenance per insert: trace it and capture the check query beside it.

## Reference snippet
```sql
SELECT id, status FROM orders
WHERE status = 'open'
ORDER BY id
FETCH FIRST 50 ROWS ONLY;
```

## Acceptance
- All six exercises finish with artifacts a reviewer can open.
- The write-up quotes the rule that B-tree indexes accelerate equality and range lookups on leading columns.
- A second run reproduces identical row counts.
- Each exercise names its own failure signal.

## Reflection
- Which step surprised you, and which fact explains it?
- What indexing shortcut would you forbid on a shared database?
- The reflection stays inside the project folder beside the scripts.

## Setup checklist
- This work runs in a scratch schema isolated from any shared database.
- Seed rows for orders and order_lines loaded and counted.
- Surprises worth quoting get jotted in an open notes file.
- Confirm the rollback or re-seed path before the first edit.

## Hand-off
- Tag the finished scripts folder; the next lab can pick it up without re-reading everything.
- Surprises survive the handoff because the notes file goes to whoever reruns the exercises.
- Only mark the checklist done once a peer has rerun all scripts without edits.

