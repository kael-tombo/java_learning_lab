# PLSQL Fundamentals — Mini Project

## Brief
Six focused exercises on PL/SQL DECLARE, BEGIN, EXCEPTION, and END blocks with cursors, each ending with a visible artifact and a one-line explanation.

## Setup
Prepare seed rows for clerks and tasks, sized so the block output fits on one screen.

## Exercises
1. Exercise on greeting block declaring and printing a clerk name: draft it, then explain the result to a reviewer aloud.
2. Exercise on exception handler catching a missing-task lookup: load it and file the script where the next step finds it.
3. Exercise on explicit cursor looping over open clerk tasks: run it while keeping every statement re-runnable.
4. Exercise on parameterized cursor filtering tasks by clerk id: shape it and record what changes in the output.
5. Exercise on transaction-control note placing COMMIT after the loop: assemble it, then note the one surprise worth remembering.
6. Exercise on cursor-attribute check using percent-NOTFOUND to exit cleanly: compose it and capture the check query beside it.

## Reference snippet
```sql
DECLARE
  v_name VARCHAR2(100);
BEGIN
  SELECT name INTO v_name
  FROM clerks
  WHERE id = 1;
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    v_name := 'none';
END;
/
```

## Acceptance
- All six exercises finish with artifacts a reviewer can open.
- The write-up quotes the rule that DECLARE opens the block for variables before executable statements begin.
- A second run reproduces identical row counts.
- Each exercise names its own failure signal.

## Reflection
- Which step surprised you, and which fact explains it?
- What block shortcut would you forbid on a shared database?
- The reflection stays inside the project folder beside the scripts.

## Setup checklist
- A scratch schema is set aside for this work, away from shared databases.
- Seed rows for clerks and tasks loaded and counted.
- Notes file stays open for anything surprising worth quoting.
- Rollback or re-seed: that path is confirmed before edits begin.

## Hand-off
- Tag the scripts folder when done, so the next lab starts without re-reading all files.
- The notes file goes to whoever reruns the exercises, and the surprises survive the handoff that way.
- A peer reruns every script without edits before this checklist is marked done.

