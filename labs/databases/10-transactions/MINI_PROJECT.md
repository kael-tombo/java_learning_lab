# Transactions — Mini Project

## Brief
Six focused exercises on ACID behavior, run under READ COMMITTED for the baseline and REPEATABLE READ for the comparison, each ending with a visible artifact and a one-line explanation.

## Setup
Prepare seed rows for accounts and transfers, sized so every result fits on one screen.

## Exercises
1. Exercise on transfer script moving funds between two accounts atomically: compose it and record what changes in the output.
2. Exercise on dirty-read demonstration blocked by READ COMMITTED: frame it then note the one surprise worth remembering.
3. Exercise on non-repeatable-read comparison across the two isolation levels: trace it and capture the check query beside it.
4. Exercise on lost-update drill with two concurrent debits: draft it then explain the result to a reviewer aloud.
5. Exercise on rollback drill restoring balances after a mid-transfer fault: load it and file the script where the next step finds it.
6. Exercise on isolation-choice note justifying the transfer default: run it while keeping every statement re-runnable.

## Reference snippet
```sql
UPDATE accounts SET balance = balance - 50
WHERE id = 1;
UPDATE accounts SET balance = balance + 50
WHERE id = 2;
COMMIT;
```

## Acceptance
- All six exercises finish with artifacts a reviewer can open.
- The write-up quotes the atomicity group so partial transfers never persist.
- A second run reproduces identical row counts.
- Each exercise names its own failure signal.

## Reflection
- Which step surprised you, and which fact explains it?
- What shortcut would you forbid on a shared database?
- The reflection stays inside this folder beside the scripts.

## Setup checklist
- A scratch schema is set aside for this work, away from shared databases.
- Seed rows for accounts and transfers loaded and counted.
- Surprises worth quoting get jotted in an open notes file.
- Confirm the rollback or re-seed path before the first edit.

## Hand-off
- Tag the scripts folder when done, so the next lab starts without re-reading all files.
- Whoever reruns the exercises receives the notes file, keeping the surprises alive through the handoff.
- Checklist completion waits for a peer rerun of every script, unedited.
