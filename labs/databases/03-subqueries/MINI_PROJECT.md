# Subqueries — Mini Project

## Brief
Six focused exercises on scalar, IN and EXISTS, plus derived-table subqueries, each ending with a visible artifact and a one-line explanation.

## Setup
Prepare seed rows for courses and results, sized so the query results fit on one screen.

## Exercises
1. Exercise on scalar subquery fetching the top course score inline: load it and record what changes in the output.
2. Exercise on IN-list filter for results in a chosen course set: run it, then note the one surprise worth remembering.
3. Exercise on EXISTS check for courses that actually have results: shape it and capture the check query beside it.
4. Exercise on NOT EXISTS hunt for courses with zero results: assemble it, then explain the result to a reviewer aloud.
5. Exercise on derived table computing per-course averages before filtering: compose it and file the script where the next step finds it.
6. Exercise on correlated rewrite comparing scalar versus EXISTS plans: frame it while keeping every statement re-runnable.

## Reference snippet
```sql
SELECT id FROM courses
WHERE EXISTS (
  SELECT 1 FROM results r
  WHERE r.course_id = courses.id
)
ORDER BY id
FETCH FIRST 20 ROWS ONLY;
```

## Acceptance
- All six exercises finish with artifacts a reviewer can open.
- The write-up quotes the rule that a scalar subquery returns one value and fits inside a SELECT or WHERE clause.
- A second run reproduces identical row counts.
- Each exercise names its own failure signal.

## Reflection
- Which step surprised you, and which fact explains it?
- What subquery shortcut would you forbid on a shared database?
- The reflection stays inside the project folder beside the scripts.

## Setup checklist
- Reserve a scratch schema just for this work and keep shared databases out of it.
- Seed rows for courses and results loaded and counted.
- Notes file stays open for anything surprising worth quoting.
- Rollback or re-seed: that path is confirmed before edits begin.

## Hand-off
- Tag the finished scripts folder; the next lab can pick it up without re-reading everything.
- The notes file goes to whoever reruns the exercises, and the surprises survive the handoff that way.
- A peer reruns every script without edits before this checklist is marked done.

