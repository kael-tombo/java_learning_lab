# Cassandra NoSQL — Mini Project

## Scenario
A teammate needs a runnable example of Cassandra partition keys with QUORUM read and write reasoning by end of day, small enough to review in one sitting.

## What you ship
A scripted walkthrough covering partition design and consistency checks, with seed data, ordered steps, and a verification section at the end.

## Working sequence
1. First, shape the partition-key design keeping one device-day per partition, and file the script where the next step finds it.
2. Next, assemble the clustering-order sketch sorting readings by timestamp, while keeping every statement re-runnable.
3. Then, compose the QUORUM write walkthrough on a three-replica sketch, and record what changes in the output.
4. After that, frame the QUORUM read walkthrough overlapping the write set, then note the one surprise worth remembering.
5. Further, trace the hot-partition review splitting one oversized device feed, and capture the check query beside it.
6. Finally, draft the tombstone-awareness note on deleting old telemetry, then explain the result to a reviewer aloud.

## Reference snippet
```text
CREATE TABLE telemetry.device_day (
  device TEXT, day TEXT, ts TIMESTAMP,
  v DOUBLE, PRIMARY KEY ((device, day), ts)
);
```

## Verification
- Rerun the full sequence twice; the second pass must stay green.
- Show how the partition key decides which nodes store each telemetry row, and point to the line where that shows up in the results.
- Demonstrate that wide rows cluster time-ordered readings inside one partition, backed by one concrete observation.
- Keep the telemetry row counts consistent across every rerun.

## Concept tie-in
This drill exercises the consistency rules end to end: quorum reads and writes overlap on enough replicas to agree.

## Setup checklist
- Shared databases stay untouched because a scratch schema is reserved here.
- Seed rows for devices and telemetry loaded and counted.
- An open notes file catches surprises worth quoting later.
- Confirm the rollback or re-seed path before the first edit.

## Next step
Carry these scripts into the real-world project as the starting scaffold.

## Hand-off
- Tag the finished scripts folder; the next lab can pick it up without re-reading everything.
- Whoever reruns the exercises receives the notes file, keeping the surprises alive through the handoff.
- The checklist gets its done mark after a peer reruns every script, edits free.

