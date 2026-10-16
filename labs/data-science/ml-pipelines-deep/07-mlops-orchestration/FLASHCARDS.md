# MLOps Orchestration - Flashcards

Q: What is a DAG run? A: Tasks ordered by dependencies, branches in parallel.
Q: Define idempotent task. A: Rerun with same inputs gives identical outputs.
Q: Backoff formula? A: min(cap, base*2^n) per attempt.
Q: Why add jitter? A: To desynchronize retries across tasks.
Q: Cron vs event trigger? A: Fixed cadence vs reacting to arrivals or signals.
Q: What is backfill? A: Replaying past windows after a fix.
Q: Backfill writes where? A: Versioned outputs, never live paths.
Q: Artifact lineage pointers? A: Data version, code commit, parameters, environment.
Q: Promotion rule? A: Overall lift plus per-slice no-regression.
Q: Data-validation gate checks? A: Schema, ranges, null rates before training.
Q: Retry which failures? A: Transient only; validation fails fast.
Q: Rerun diverged: cause? A: Unpinned dependency or missing seed.
Q: Separate queues why? A: So backfills never starve scheduled runs.
Q: Promotion record holds? A: Who, when, and which lineage pointer shipped.
Q: Gate failure effect? A: Run stops; production routing stays untouched.
Q: Topological order guarantees? A: Parents run before children, always.
Q: Cycle policy? A: Forbidden; break with explicit iteration constructs.
Q: Attempt limit why? A: Bounds worst-case stall per task.
Q: Total wait over k retries? A: Partial sum of the capped schedule.
Q: Base 1 s uncapped six waits? A: 1+2+4+8+16+32 = 63 s.
Q: Jitter shape? A: Bounded random spread around the schedule.
Q: Transient vs deterministic? A: Retry the first; fail fast on the second.
Q: Run id uses? A: Keys outputs, resume points, audit joins.
Q: Overwrite vs append? A: Overwrite is idempotent; append duplicates.
Q: Promotion flag pattern? A: Flag-then-act, once, outside retried tasks.
Q: Attempt records? A: Counts and backoff used, kept for postmortems.
Q: Fingerprint inputs? A: Data version, code commit, params, environment.
Q: Snippet fingerprint? A: 1047179432, equal across identical reruns.
Q: Gate conjunction? A: Overall lift AND every slice bar; one veto blocks.
Q: Snippet gate verdict? A: Overall passes (+0.025 vs +0.010) but slice 2 vetoes.
Q: Absolute vs ratio bars? A: Absolute drops protect small slices.
Q: Cron staleness bound? A: Period plus run duration.
Q: Event staleness bound? A: Detection delay instead of clock period.
Q: Poison partition path? A: Quarantine aside with owner notification.
Q: Staging promotion? A: Full gates on mirrored traffic before production.
Q: Zombie schedule? A: Dead cron entry launching duplicate runs.
