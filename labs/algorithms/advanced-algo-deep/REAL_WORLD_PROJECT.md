# REAL_WORLD_PROJECT — Advanced Algorithms Deep Track
> Algorithm-review board pipeline: every production proposal ships with a paradigm card (guarantee type, bounds, measured limits, fallback) generated from the capstone battery.

## System and inputs
- Proposal template requires: problem statement, chosen paradigm, guarantee class (exact/bounded-error/empirical), measured limiter table, and fallback path.
- Battery runs the ten reference checks plus the proposer's instance as a CI gate.
- Review board meets weekly with the paradigm cards as the agenda packet.

## Design
- CI gate executes the capstone runner; reference-output drift fails the build (catches environment/JDK surprises).
- Proposer instances run under time and memory caps derived from their own claimed bounds; overruns fail with the cap arithmetic shown.
- Fallback registry maps each paradigm to its degraded mode (heuristic for exact, exact-sample audit for sketches, previous version for indexes).
- Decision log records accept/conditional/reject with the limiter cited.

## Metrics
- Proposal lead time and first-pass acceptance rate by paradigm.
- Cap-overrun rate (claims vs measured) tracked as an organizational calibration signal.
- Fallback invocation rate in production per paradigm.
- Reference-battery green rate (environment stability).

## Failure modes
- Claim without measurement: template rejects missing limiter tables at submission, not at review.
- Environment drift breaking reference outputs: battery failure pages the platform owner, not the proposer.
- Paradigm mismatch (exact method proposed past its n ceiling): cap arithmetic check fails the gate with the table row cited.
- Review rubber-stamping: decision log audited quarterly for limiter citations.

## Rollout
1. Pilot with two teams; calibrate caps from their first measured tables.
2. Require cards for all new algorithmic services; grandfather existing ones with a one-quarter grace period.
3. Quarterly review of calibration data (claims vs measured) published to engineering.

## Acceptance criteria
1. Ten reference outputs verify through the CI gate path on every run.
2. Oversized-instance test fails the gate with cap arithmetic attached.
3. Missing-limiter submission is rejected at intake (test included).
4. Fallback registry covers all ten paradigms with a named degraded mode each.
5. Decision log shows limiter citations on sampled entries.

## Cost and contract notes
- Review-board operating cost tracked per proposal; calibration data (claims vs measured) published quarterly.
- Cap-overrun failures costed to the proposing team as rework days, keeping estimates honest.
- Battery compute (ten references per CI run) budgeted in the platform CI allocation.
- Contract: paradigm cards are versioned documents; fallback registry entries carry owner and drill date.
