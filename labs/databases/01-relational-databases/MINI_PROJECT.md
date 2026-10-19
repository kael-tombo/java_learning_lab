# Relational Databases — Mini Project

## Objective
Produce a working relational modeling exercise built on primary keys, foreign keys, and normal forms, in about ninety minutes, ending with scripts a peer can rerun.

## Core facts
- A primary key uniquely identifies each row and never repeats across the table. Every schema decision below leans on that guarantee.
- A foreign key references a parent primary key and preserves referential integrity — the constraint the design has to hold under delete and update pressure.
- Third normal form removes transitive dependencies so facts live in exactly one place; that is the bar the finished model has to meet.

## Build
Create one scratch schema dedicated to this modeling drill, seed a handful of rows, then work the task list in order.

## Task list
1. Draft the author-book key diagram with sample rows, and record what changes in the output.
2. Load the 1NF cleanup of a repeating-group spreadsheet, then note the one surprise worth remembering.
3. Run the 2NF split that removes the partial dependency on book category, and capture the check query beside it.
4. Shape the 3NF split that moves publisher city out of the book row, then explain the result to a reviewer aloud.
5. Assemble the referential-actions sketch for deleting an author who still has books, and file the script where the next step finds it.
6. Compose the row-count reconciliation query that runs after each normalization step, while keeping every statement re-runnable.

## Reference snippet
```sql
SELECT id FROM authors
WHERE id IS NOT NULL
ORDER BY id
FETCH FIRST 10 ROWS ONLY;
```

## Checks
- Every script reruns cleanly on a fresh schema without manual edits.
- Row counts reconcile before and after each transformation step.
- One observed modeling behavior is written down with its cause.
- The snippet above executes (or the sketch reads correctly) against the seeded authors data.

## Stretch
- Break one modeling assumption deliberately, then document the error message verbatim.
- Remove one helper and show the exercise still passes without it.

## Done
The folder holds scripts, seed data, and a short note naming the trickiest step.

## Hand-off
- Tag the finished scripts folder so the next lab picks it up without re-reading every file.
- Hand the notes file to whoever reruns the exercises, so the surprises survive the handoff.
- Mark this checklist done only after a peer has rerun every script without edits.

