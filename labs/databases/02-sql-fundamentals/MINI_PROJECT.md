# SQL Fundamentals — Mini Project

## Objective
Produce a working exercise on constraints, keys, and the DML basics, in about ninety minutes, ending with scripts a peer can rerun.

## Core facts
- NOT NULL plus CHECK constraints reject bad data at the gate. Every change below has to pass through them.
- INSERT, UPDATE, and DELETE change data while SELECT only reads it — that split shapes when checks fire.
- A transaction groups DML statements so they commit or roll back together; that is the acceptance bar for the drills.

## Build
Create one scratch schema dedicated to this drill, seed a handful of rows, then work the task list in order.

## Task list
1. Shape the student table with a primary key and email uniqueness, then explain the result to a reviewer aloud.
2. Assemble the enrollment foreign key with a documented delete rule, and file the script where the next step finds it.
3. Compose the CHECK constraint bounding grades to a legal range, while keeping every statement re-runnable.
4. Frame the single-row INSERT statements for three seed students, and record what changes in the output.
5. Trace the guarded UPDATE that touches exactly one enrollment row, then note the one surprise worth remembering.
6. Draft the COMMIT and ROLLBACK drill on a scratch enrollment, and capture the check query beside it.

## Reference snippet
```sql
SELECT id FROM students
WHERE id IS NOT NULL
ORDER BY id
FETCH FIRST 10 ROWS ONLY;
```

## Checks
- Every script reruns cleanly on a fresh schema without manual edits.
- Row counts reconcile before and after each transformation step.
- One observed constraint behavior is written down with its cause.
- The snippet above executes (or the sketch reads correctly) against the seeded students data.

## Stretch
- Break one constraint deliberately, then document the error message verbatim.
- Remove one helper and show the exercise still passes without it.

## Done
The folder holds scripts, seed data, and a short note naming the trickiest step.

## Hand-off
- Tag the finished scripts folder so the next lab picks it up without re-reading every file.
- Hand the notes file to whoever reruns the exercises, so the surprises survive the handoff.
- Mark this checklist done only after a peer has rerun every script without edits.

