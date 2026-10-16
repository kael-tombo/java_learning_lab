# MLOps Orchestration - Exercises

1. Run A07Backoff with base 500 ms and cap 8000 ms; print the schedule and total wait over 6 attempts.
   - Expect 500, 1000, 2000, 4000, 8000, 8000 with total 23500 ms.
2. Extend B07Lineage with an environment pin string; show the fingerprint changing when the pin changes.
   - Print both fingerprints to prove the lineage pointer covers the environment.
3. In C07Gate, fix slice 2 to 0.819 and re-evaluate promotion. State which gate flipped the verdict.
   - Expect promote to turn true; the slice no-regression bar was the veto.
4. Make a non-idempotent counter task idempotent by keying writes on run id.
   - Run it twice with the same id and show identical outputs.
5. Implement a cron-vs-event trigger table: given three scenarios, choose and justify the trigger.
   - Cover steady retraining, new-partition arrival, and drift-alert response.
6. Write a backfill driver: replay days 1-5 in order into versioned paths without touching a live path.
   - Print each window's output path to show the versioning.
7. Add a data-validation gate: reject a partition with more than 5% nulls before training starts.
    - Demonstrate one passing and one failing partition.
8. Convert a wall-clock schedule to arrival-gated triggers: given five partition
   landing times and one fixed cron tick, show which runs waited and which raced.
    - Expect the cron-only design to race twice; report both windows.
9. Quarantine a poison partition: route one corrupt day aside while days around it
   train normally, then show the run record marking the quarantine.
    - Print the quarantine path and the owner notification line.
10. Reproduce the gate veto: vary slice 2 across three values and tabulate promote
    true/false beside the failing bar each time.
    - Expect exactly one flip point; name the bar that vetoes elsewhere.
11. Verify total-wait arithmetic: compute the partial sum of a six-attempt capped
    schedule from base and cap, then confirm the cap truncates the tail.
    - Show each term and mark where the cap first binds.
12. Freeze an evaluation set: hash its rows, then show a gate verdict changing when
    one row is swapped and holding when rerun identically.
    - Print both hashes and both verdicts to prove set-sensitivity.
13. Audit a promotion record: given a run with lineage pointer, check data version,
    code commit, parameters, and environment pin are all present.
    - Reject the record in writing if any pointer is missing, naming the gap.
14. Starve-then-fix queues: run a backfill beside scheduled work on one shared queue,
    measure scheduled wait, then repeat on separated queues.
    - Expect scheduled wait to collapse; report both waits.
   - Demonstrate one passing and one failing partition.

## Submission check
- All programs compile with `javac --release 21 -encoding UTF-8` and print pure ASCII.
