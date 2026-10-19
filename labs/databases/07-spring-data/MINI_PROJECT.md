# Spring Data — Mini Project

## Objective
Produce a working exercise on Spring Data repository derivation and query methods in about ninety minutes, ending with scripts a peer can rerun.

## Core facts
- Derived query methods translate method names into generated queries. Every finder below leans on that translation.
- Paging and sorting parameters keep large result sets bounded — that is how the listings behave under checks.
- Custom queries override derivation when method names grow unreadable; that is the acceptance bar.

## Build
Create one scratch schema dedicated to this drill, seed a handful of rows, then work the task list in order.

## Task list
1. Assemble the driver repository with a derived status finder, and record what changes in the output.
2. Compose the route search combining two criteria in one name, then note the one surprise worth remembering.
3. Frame the paged driver listing with explicit sort order, and capture the check query beside it.
4. Trace the custom query replacing an unreadable derived name, then explain the result to a reviewer aloud.
5. Draft the null-handling review for optional finder parameters, and file the script where the next step finds it.
6. Load the naming-boundary note marking when derivation stops paying off, while keeping every statement re-runnable.

## Reference snippet
```text
interface DriverRepo {
  findByStatusOrderByNameAsc(status, page)
  // custom query replaces overlong names
}
```

## Checks
- Every script reruns cleanly on a fresh schema without manual edits.
- Row counts reconcile before and after each transformation step.
- One observed derivation behavior is written down with its cause.
- The snippet above executes (or the sketch reads correctly) against the seeded drivers data.

## Stretch
- Break one derivation assumption deliberately, then document the error message verbatim.
- Remove one helper and show the exercise still passes without it.

## Done
The folder holds scripts, seed data, and a short note naming the trickiest step.

## Hand-off
- Tag the finished scripts folder so the next lab picks it up without re-reading every file.
- Hand the notes file to whoever reruns the exercises, so the surprises survive the handoff.
- Mark this checklist done only after a peer has rerun every script without edits.

