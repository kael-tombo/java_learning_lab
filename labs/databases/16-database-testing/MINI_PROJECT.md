# Database Testing — Mini Project

## Objective
Produce a working exercise on database tests with fixtures, transactions, and migration checks in about ninety minutes, ending with scripts a peer can rerun.

## Core facts
- Fixtures load a known dataset so assertions stay deterministic. Every case below leans on that determinism.
- Rolling each test back keeps suites independent and repeatable — that is how the suite behaves under checks.
- Migration tests prove upgrades and downgrades both succeed; that is the acceptance bar.

## Build
Create one scratch schema dedicated to this drill, seed a handful of rows, then work the task list in order.

## Task list
1. Draft the fixture script seeding three deterministic rows, and record what changes in the output.
2. Load the rollback-wrapped test proving isolation between cases, then note the one surprise worth remembering.
3. Run the constraint test asserting duplicate keys fail loudly, and capture the check query beside it.
4. Shape the migration up-and-down test on a scratch copy, then explain the result to a reviewer aloud.
5. Assemble the data-volume test with a generated hundred-row batch, and file the script where the next step finds it.
6. Compose the flaky-order hunt fixing one order-dependent assertion, while keeping every statement re-runnable.

## Reference snippet
```text
fixture -> three deterministic rows
test -> run inside a transaction, then roll back
migration check -> upgrade and downgrade on scratch
```

## Checks
- Every script reruns cleanly on a fresh schema without manual edits.
- Row counts reconcile before and after each transformation step.
- One observed suite behavior is written down with its cause.
- The snippet above executes (or the sketch reads correctly) against the seeded fixtures data.

## Stretch
- Break one fixture assumption deliberately, then document the error message verbatim.
- Remove one helper and show the exercise still passes without it.

## Done
The folder holds scripts, seed data, and a short note naming the trickiest step.

## Hand-off
- Tag the finished scripts folder so the next lab picks it up without re-reading every file.
- Hand the notes file to whoever reruns the exercises, so the surprises survive the handoff.
- Mark this checklist done only after a peer has rerun every script without edits.

