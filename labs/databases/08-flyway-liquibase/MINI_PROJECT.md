# Flyway and Liquibase — Mini Project

## Scenario
A teammate needs a runnable example of versioned Flyway and Liquibase schema migrations by end of day, small enough to review in one sitting.

## What you ship
A scripted migration walkthrough with seed data, ordered steps, and a verification section at the end.

## Working sequence
1. First, trace the V1 migration creating the ledger table, and file the script where the next step finds it.
2. Next, draft the V2 migration adding the entry foreign key, while keeping every statement re-runnable.
3. Then, load the repeatable view migration for a balance summary, and record what changes in the output.
4. After that, run the undo script reversing the entry column addition, then note the one surprise worth remembering.
5. Further, shape the checksum-failure drill after editing an applied migration, and capture the check query beside it.
6. Finally, assemble the baseline note for adopting migrations on an existing database, then explain the result to a reviewer aloud.

## Reference snippet
```text
V1__create_ledger.sql  -> CREATE TABLE ledgers (...)
V2__add_entry_fk.sql  -> ALTER TABLE entries ADD CONSTRAINT ...
R__balance_view.sql -> repeatable balance view
```

## Verification
- Rerun the full sequence twice; the second pass must stay green.
- Show how migrations apply in version order and record checksums after success, and point to the line where that shows up in the results.
- Demonstrate that repeatable migrations re-run when their checksum changes, backed by one concrete observation.
- Keep the entries row counts consistent across every rerun.

## Concept tie-in
This drill exercises the migration lifecycle end to end: down scripts or undo files define the path back from a bad change.

## Setup checklist
- Reserve a scratch schema just for this work and keep shared databases out of it.
- Seed rows for ledgers and entries loaded and counted.
- An open notes file catches surprises worth quoting later.
- Before editing anything, the rollback or re-seed path is confirmed.

## Next step
Carry these scripts into the real-world project as the starting scaffold.

## Hand-off
- The finished scripts folder gets tagged so the next lab skips re-reading every file.
- Whoever reruns the exercises receives the notes file, keeping the surprises alive through the handoff.
- Only mark the checklist done once a peer has rerun all scripts without edits.

