# REAL_WORLD_PROJECT — Classical Simulation of Quantum Circuits
> Shared teaching-lab simulator service: queued state-vector jobs with a memory estimator gate, per-course quotas, and reproducible seeded sampling.

## System and inputs
- Students submit (circuit file, qubit count, shots, seed) through a course portal; service caps full simulation at a configured n (default 20).
- Estimator runs first: bytes = 2^n x 16 plus shot-memory; jobs over cap are rejected with the figure, never attempted.
- Reference circuits (H|0>, Bell pair, GHZ-3) run as a health gate on every deploy.

## Design
- Queue with per-course fair share; one worker simulates one job at a time to bound peak RAM.
- Seeded sampling only: every histogram is reproducible from (circuit, shots, seed); seed logged with results.
- Result bundle: final probabilities for n <= 8, histogram otherwise, estimator figure, worker memory high-water mark.

## Metrics
- Estimator accuracy: predicted bytes vs worker high-water mark per job (ratio dashboard).
- Queue wait p95 per course and rejection rate with byte figures attached.
- Health-gate pass/fail on every deploy (blocks promotion on mismatch).
- Quota consumption per course per week.

## Failure modes
- Under-estimated memory (bookkeeping overhead): cap set 20 percent below worker RAM; estimator figure includes the overhead factor, reviewed termly.
- Student submits n = 100 expecting magic: rejection message shows the byte figure and suggests estimate-only mode.
- RNG seed reuse across assignments: portal requires explicit seed; default seed flagged in the UI as non-independent.
- Worker OOM despite cap: cgroup limit kills the worker, job marked failed-clean with the high-water mark recorded.

## Rollout
1. Pilot with one course on historical circuits; compare histograms to reference outputs.
2. Open to all courses with quotas; publish the estimator table in the docs.
3. Termly review of cap and overhead factor from the accuracy dashboard.

## Acceptance criteria
1. Health gate reproduces Bell probs 0.5/0/0/0.5 and the n=30 byte figure on every deploy.
2. An n=50 job is rejected pre-queue with its byte estimate in the message.
3. Same (circuit, shots, seed) twice gives byte-identical histograms.
4. OOM-killed worker recovers to accept the next job without manual restart.
5. Docs page shows the memory table with the classical-simulation-only disclaimer.

## Cost and contract notes
- Worker sizing starts from the estimator table: cap = 80 percent of worker RAM divided by 16 bytes, floored to a whole qubit count.
- Course quotas priced in estimated GB-seconds from the accuracy dashboard, reviewed termly.
- Result bundles embed (circuit hash, shots, seed, estimator figure) so any histogram is re-derivable.
- Rejection messages always include the byte figure and the estimate-only alternative, never a bare error code.
