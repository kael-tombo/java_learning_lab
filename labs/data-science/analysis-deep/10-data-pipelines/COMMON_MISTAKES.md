# Common Mistakes - Data Pipelines

1. Append sinks with retries. Duplicates on every replay - merge by key
   or accept double-counting as designed (never accept it).
2. Validating after transforming. Dirty input becomes mysterious metric
   drift; gate raw landings first.
3. Breaking schemas casually. Type tweaks and renames need versioned
   migration, not Friday deploys.
4. Rerunning against live tables. Ad-hoc reruns double-count; replay to
   staging, diff, then promote.
5. Warn-only quality checks. Bouncers who never bounce admit everything -
   quarantine loudly on breach.
6. No late-data policy. Arrival-time-by-default corrupts windows when
   events run late; declare event-time handling upfront.
7. Wall clocks in transforms. Non-determinism kills replay testing; event
   time only in business logic.
8. Ignoring small drift. A 0.375 drift today is a regime change next
   month; trend the check outputs, not just the verdicts.
9. Cyclic "DAGs." A task waiting on its own output deadlocks or loops;
   enforce acyclicity at build time.
10. Unlogged runs. No version/range/counts log means month-old numbers
    are indefensible - log every run identically.

11. Sampling checks on skewed data. A 1% sample that misses the one bad
    partition reports green over corruption - stratify samples by source
    partition or check in full; state which.
12. Versioning data but not code. Replaying v2 data with v1 logic (or the
    reverse) during incidents produces confident garbage - pin code version
    in every run log and enforce it on replay.

Rule of thumb: if the run log cannot reproduce the number, the number is
hearsay - log version, range, and counts every time.

13. Testing with toy-shaped data. Six clean rows never catch skew,
    null storms, or late partitions - replay a production week through
    staging before trusting any green check.
