# Joins — Mini Project

## Brief
Six focused exercises on INNER, LEFT, RIGHT, and FULL joins plus lateral reads, each ending with a visible artifact and a one-line explanation.

## Setup
Prepare seed rows for teams and players, sized so the join results fit on one screen.

## Exercises
1. Exercise on team roster via INNER JOIN on team id: frame it, then explain the result to a reviewer aloud.
2. Exercise on bench report via LEFT JOIN exposing players without teams: trace it and file the script where the next step finds it.
3. Exercise on FULL JOIN reconciliation of two independently kept lists: draft it while keeping every statement re-runnable.
4. Exercise on per-team top scorer using a lateral-style correlated lookup: load it and record what changes in the output.
5. Exercise on accidental fan-out diagnosis after joining through a multi-valued bridge: run it, then note the one surprise worth remembering.
6. Exercise on NULL-audit query counting unmatched rows on each side: shape it and capture the check query beside it.

## Reference snippet
```sql
SELECT t.id, p.id
FROM teams t
INNER JOIN players p
  ON p.team_id = t.id
WHERE t.active = 1
ORDER BY t.id
FETCH FIRST 20 ROWS ONLY;
```

## Acceptance
- All six exercises finish with artifacts a reviewer can open.
- The write-up quotes the rule that an inner join keeps only rows with a match on both sides.
- A second run reproduces identical row counts.
- Each exercise names its own failure signal.

## Reflection
- Which step surprised you, and which fact explains it?
- What join shortcut would you forbid on a shared database?
- The reflection stays inside the project folder beside the scripts.

## Setup checklist
- A scratch schema is set aside for this work, away from shared databases.
- Seed rows for teams and players loaded and counted.
- Notes file stays open for anything surprising worth quoting.
- The first edit waits until the rollback or re-seed path is confirmed.

## Hand-off
- Tag the finished scripts folder; the next lab can pick it up without re-reading everything.
- Whoever reruns the exercises receives the notes file, keeping the surprises alive through the handoff.
- The checklist gets its done mark after a peer reruns every script, edits free.

