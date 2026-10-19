# MongoDB — Mini Project

## Scenario
A teammate needs a runnable example of MongoDB document modeling and find query patterns by end of day, small enough to review in one sitting.

## What you ship
A scripted walkthrough covering the document shapes and their queries, with seed data, ordered steps, and a verification section at the end.

## Working sequence
1. First, load the customer document with an embedded address history, and file the script where the next step finds it.
2. Next, run the ticket referencing its customer instead of embedding, while keeping every statement re-runnable.
3. Then, shape the find query filtering tickets by priority and state, and record what changes in the output.
4. After that, assemble the projection returning only ticket id, title, and state, then note the one surprise worth remembering.
5. Further, compose the array-field query matching any tag in a ticket, and capture the check query beside it.
6. Finally, frame the schema-evolution note adding an optional SLA field, then explain the result to a reviewer aloud.

## Reference snippet
```text
db.tickets.find({ priority: "high" }, { title: 1, state: 1 })
db.tickets.createIndex({ state: 1 })
db.customers.countDocuments({})
```

## Verification
- Rerun the full sequence twice; the second pass must stay green.
- Show how documents store nested fields together so one read returns the whole aggregate, and point to the line where that shows up in the results.
- Demonstrate that embedding suits contained children while referencing suits shared entities, backed by one concrete observation.
- Keep the tickets row counts consistent across every rerun.

## Concept tie-in
This drill exercises the patterns end to end: find queries filter on fields and project only the needed shape.

## Setup checklist
- Reserve a scratch schema just for this work and keep shared databases out of it.
- Seed rows for customers and tickets loaded and counted.
- Anything surprising enough to quote goes into the open notes file.
- The first edit waits until the rollback or re-seed path is confirmed.

## Next step
Carry these scripts into the real-world project as the starting scaffold.

## Hand-off
- A tagged scripts folder lets the next lab skip re-reading every file.
- The notes file changes hands with the exercises, and the surprises survive with it.
- Only mark the checklist done once a peer has rerun all scripts without edits.

