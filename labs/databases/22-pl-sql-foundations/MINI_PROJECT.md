# PL SQL Foundations — Mini Project

## Scenario
A teammate needs a runnable example of PL/SQL procedures, functions, and explicit transaction control by end of day, small enough to review in one sitting.

## What you ship
A scripted walkthrough covering the subprograms and their boundaries, with seed data, ordered steps, and a verification section at the end.

## Working sequence
1. First, load the shift procedure assigning one staff member explicitly, and file the script where the next step finds it.
2. Next, run the bonus function computing pay from shift count, while keeping every statement re-runnable.
3. Then, shape the parameter-mode table documenting each argument direction, and record what changes in the output.
4. After that, assemble the explicit COMMIT placed after a full shift batch, then note the one surprise worth remembering.
5. Further, compose the ROLLBACK handler restoring shifts after a roster fault, and capture the check query beside it.
6. Finally, frame the caller-permissions note on definer versus invoker choice, then explain the result to a reviewer aloud.

## Reference snippet
```sql
DECLARE
  v_name VARCHAR2(100);
BEGIN
  SELECT name INTO v_name
  FROM f_staff
  WHERE id = 1;
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    v_name := 'none';
END;
/
```

## Verification
- Rerun the full sequence twice; the second pass must stay green.
- Show how procedures perform actions while functions compute and return values, and point to the line where that shows up in the results.
- Demonstrate that IN, OUT, and IN OUT modes define parameter direction, backed by one concrete observation.
- Keep the f_shifts row counts consistent across every rerun.

## Concept tie-in
This drill exercises the boundary rules end to end: explicit commit and rollback mark the transaction boundary.

## Setup checklist
- Reserve a scratch schema just for this work and keep shared databases out of it.
- Seed rows for f_staff and f_shifts loaded and counted.
- Surprises worth quoting get jotted in an open notes file.
- Rollback or re-seed: that path is confirmed before edits begin.

## Next step
Carry these scripts into the real-world project as the starting scaffold.

## Hand-off
- A tagged scripts folder lets the next lab skip re-reading every file.
- The notes file changes hands with the exercises, and the surprises survive with it.
- A peer reruns every script without edits before this checklist is marked done.

