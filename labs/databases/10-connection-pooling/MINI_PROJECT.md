# Connection Pooling — Mini Project

## Scenario
A teammate needs a runnable example of pool sizing with minimum, maximum, and idle eviction by end of day, small enough to review in one sitting.

## What you ship
A scripted walkthrough covering the sizing worksheet and eviction checks, with seed data, ordered steps, and a verification section at the end.

## Working sequence
1. First, run the pool sizing worksheet deriving min and max from measured concurrency, then note the one surprise worth remembering.
2. Next, shape the idle-timeout experiment proving eviction reclaims leases, and capture the check query beside it.
3. Then, assemble the wait-queue drill observing checkout under saturation, then explain the result to a reviewer aloud.
4. After that, compose the leak-hunt review tracing one unclosed session lease, and file the script where the next step finds it.
5. Further, frame the timeout tuning separating connect, checkout, and query limits, while keeping every statement re-runnable.
6. Finally, trace the dashboard sketch tracking active, idle, and waiting counts, and record what changes in the output.

## Reference snippet
```text
min-connections: small warm reserve
max-connections: capped under database limit
idle-eviction: reclaims abandoned leases
waiting: bounded queue with timeout
```

## Verification
- Rerun the full sequence twice; the second pass must stay green.
- Show how minimum connections keep warm capacity ready for bursts, and point to the line where that shows up in the results.
- Demonstrate that maximum connections cap load so the database stays upright, backed by one concrete observation.
- Keep the leases row counts consistent across every rerun.

## Concept tie-in
This drill exercises the sizing rules end to end: idle eviction reclaims leases that sessions abandoned.

## Setup checklist
- This work runs in a scratch schema isolated from any shared database.
- Seed rows for sessions and leases loaded and counted.
- Anything surprising enough to quote goes into the open notes file.
- The rollback or re-seed path is confirmed before any edit.

## Next step
Carry these scripts into the real-world project as the starting scaffold.

## Hand-off
- A tagged scripts folder lets the next lab skip re-reading every file.
- The notes file changes hands with the exercises, and the surprises survive with it.
- The checklist gets its done mark after a peer reruns every script, edits free.

