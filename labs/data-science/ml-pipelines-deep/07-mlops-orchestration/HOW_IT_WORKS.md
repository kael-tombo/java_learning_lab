# MLOps Orchestration - How It Works

## Pipeline run
1. Trigger fires (schedule or event) and creates a run id.
2. Ingest pulls the data partition; validation gates check schema and ranges.
3. Training runs with recorded parameters and seed; artifacts are versioned.
4. Evaluation compares candidate against production on a fixed set plus slices.
5. Promotion flips serving traffic only if all gates pass.

## Retry behavior
1. A failing task waits per the backoff schedule, then retries up to a limit.
2. Because tasks are idempotent, a retry overwrites identical outputs.
3. Persistent failure marks the run failed and keeps the prior production model live.

## Backfill
1. Operator selects the affected date range and fixed code version.
2. The DAG replays those windows in order, writing versioned outputs.
3. Downstream consumers switch to corrected artifacts explicitly.

## Promotion decision
1. Overall metric must clear the lift bar; each slice must clear its no-regression bar.
2. A single failing gate blocks promotion and notifies the owner.
3. Successful promotion records who, when, and which lineage pointer went live.

## Trigger selection
1. Steady retraining takes cron; arrivals and alerts take event triggers.
2. Most systems run both: cron bounds staleness, events react to change.
3. Record which trigger fired each run for staleness audits.

## Evaluation set discipline
1. Freeze the comparison set; hash it and store the hash with the run.
2. Score candidate and production on the identical frozen rows.
3. Slice the same rows per segment for the no-regression conjunction.

## Resume after failure
1. Run store marks completed tasks; resume skips or rewrites them identically.
2. Idempotent writes make the skip-or-rewrite choice invisible downstream.
3. Attempt counts and waits persist for the postmortem record.

## Staging promotion
1. Mirror production traffic through the candidate without serving it.
2. Run full gates on the mirrored comparison before touching routing.
3. Promote to production only after staging gates and owner sign-off.
