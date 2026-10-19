# Query Optimization C — Mini Project

## Brief
Six focused exercises on join order and covering-index reasoning in the events domain, each ending with a visible artifact and a one-line explanation.

## Setup
Prepare seed rows for events and attendees, sized so the plan output fits on one screen.

## Exercises
1. Exercise on join-order rewrite leading from the selective event filter: shape it and record what changes in the output.
2. Exercise on covering index for the attendee check-in list: assemble it, then note the one surprise worth remembering.
3. Exercise on residual-predicate audit on one event report: compose it and capture the check query beside it.
4. Exercise on selective-first comparison of two join orders: frame it, then explain the result to a reviewer aloud.
5. Exercise on index-only verification noting table access disappearing: trace it and file the script where the next step finds it.
6. Exercise on maintenance note pricing each covering index on writes: draft it while keeping every statement re-runnable.

## Reference snippet
```sql
SELECT id, status FROM events
WHERE status = 'open'
ORDER BY id
FETCH FIRST 50 ROWS ONLY;
```

## Acceptance
- All six exercises finish with artifacts a reviewer can open.
- The write-up quotes the rule that join order starts from the most selective event filter.
- A second run reproduces identical row counts.
- Each exercise names its own failure signal.

## Reflection
- Which step surprised you, and which fact explains it?
- What indexing shortcut would you forbid on a shared database?
- The reflection stays inside the project folder beside the scripts.

## Setup checklist
- A scratch schema is set aside for this work, away from shared databases.
- Seed rows for events and attendees loaded and counted.
- Anything surprising enough to quote goes into the open notes file.
- The first edit waits until the rollback or re-seed path is confirmed.

## Hand-off
- Tag the scripts folder when done, so the next lab starts without re-reading all files.
- Pass the notes file to the next person rerunning the exercises so the surprises carry over.
- Peer reruns all scripts, no edits, then the checklist can be marked done.

