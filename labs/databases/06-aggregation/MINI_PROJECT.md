# Aggregation — Mini Project

## Scenario
A teammate needs a runnable GROUP BY aggregation example with legal select lists by end of day, small enough to review in one sitting.

## What you ship
A scripted walkthrough covering grouped summaries and the legality rules around them, with seed data, ordered steps, and a verification section at the end.

## Working sequence
1. First, assemble the regional sales totals grouped by region name, then note the one surprise worth remembering.
2. Next, compose the multi-key grouping by region and quarter, and capture the check query beside it.
3. Then, frame the HAVING filter keeping only regions above a revenue bar, then explain the result to a reviewer aloud.
4. After that, trace the COUNT DISTINCT tally of buyers per region, and file the script where the next step finds it.
5. Further, draft the illegal-select diagnosis fixing a well-known grouping error, while keeping every statement re-runnable.
6. Finally, load the pre-aggregation row filter comparing WHERE versus HAVING, and record what changes in the output.

## Reference snippet
```sql
SELECT region, COUNT(*) AS n, SUM(amount) AS total
FROM sales
GROUP BY region
HAVING COUNT(*) > 1
ORDER BY total DESC
FETCH FIRST 20 ROWS ONLY;
```

## Verification
- Rerun the full sequence twice; the second pass must stay green.
- Show how GROUP BY collapses rows sharing key values into summary rows, and point to the line where that shows up in the results.
- Demonstrate that every non-aggregated select column must appear in the GROUP BY list, backed by one concrete observation.
- Keep the sales row counts consistent across every rerun.

## Concept tie-in
This drill exercises the grouping rules end to end: HAVING filters groups after aggregation while WHERE filters rows before it.

## Setup checklist
- Reserve a scratch schema just for this work and keep shared databases out of it.
- Seed rows for regions and sales loaded and counted.
- An open notes file catches surprises worth quoting later.
- The first edit waits until the rollback or re-seed path is confirmed.

## Next step
Carry these scripts into the real-world project as the starting scaffold.

## Hand-off
- The finished scripts folder gets tagged so the next lab skips re-reading every file.
- Whoever reruns the exercises receives the notes file, keeping the surprises alive through the handoff.
- Peer reruns all scripts, no edits, then the checklist can be marked done.

