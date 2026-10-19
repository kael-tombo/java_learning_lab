# Database Replication — Mini Project

## Scenario
A teammate needs a runnable example of primary and replica lag measurement with failover drills by end of day, small enough to review in one sitting.

## What you ship
A scripted walkthrough covering lag probes and a failover rehearsal, with seed data, ordered steps, and a verification section at the end.

## Working sequence
1. First, draft the lag-measurement query comparing primary and replica positions, then note the one surprise worth remembering.
2. Next, load the read-routing sketch sending reports to the replica, and capture the check query beside it.
3. Then, run the failover drill promoting the replica step by step, then explain the result to a reviewer aloud.
4. After that, shape the split-brain guard requiring fenced old primaries, and file the script where the next step finds it.
5. Further, assemble the backlog review sizing replay capacity after an outage, while keeping every statement re-runnable.
6. Finally, compose the consistency note marking which reads tolerate lag, and record what changes in the output.

## Reference snippet
```text
primary: accepts writes, streams log
replica: replays log, serves stale-tolerant reads
probe: compare applied positions
```

## Verification
- Rerun the full sequence twice; the second pass must stay green.
- Show how replicas replay the primary log and always trail by some lag, and point to the line where that shows up in the results.
- Demonstrate that lag measurement compares applied positions between primary and replica, backed by one concrete observation.
- Keep the ledger_replica row counts consistent across every rerun.

## Concept tie-in
This drill exercises the failover rules end to end: failover promotes a replica and redirects writers to it.

## Setup checklist
- Reserve a scratch schema just for this work and keep shared databases out of it.
- Seed rows for ledger and ledger_replica loaded and counted.
- Surprises worth quoting get jotted in an open notes file.
- The rollback or re-seed path is confirmed before any edit.

## Next step
Carry these scripts into the real-world project as the starting scaffold.

## Hand-off
- Tag the scripts folder when done, so the next lab starts without re-reading all files.
- Surprises survive the handoff because the notes file goes to whoever reruns the exercises.
- Checklist completion waits for a peer rerun of every script, unedited.

