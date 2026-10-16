# Model Serving - Exercises

1. Run A05Latency and change the 120 ms outlier to 20. Recompute p50/p99.
   - Expect p99 to collapse toward the teens while p50 barely moves; that gap is the tail lesson.
2. Extend B05Batching with a 40 ms latency cap; print the largest batch size that fits and its throughput.
   - Solve B <= (cap - overhead)/perItem from the latency formula, then verify by running.
3. In C05Canary, double the canary traffic (canN=400, canErr=12). Recompute z.
   - Expect a similar z near 0.9: scaling both keeps the rate; error bars shrink slowly.
4. Add schema validation to a toy scorer: reject negative amounts and unknown currency codes with a logged reason.
   - Print accepted versus rejected counts on a ten-row inline dataset.
5. Write a warmup routine: load weights once, score three sample inputs, then open the traffic flag.
   - Assert the flag opens only after all three sample scores succeed.
6. Simulate stepped rollout: move traffic 10% at a time across 10 steps, checking a fake error counter each step.
   - Halt and roll back at the first step where errors exceed twice baseline.
7. Measure queueing: simulate arrivals against fixed service and record mean wait at 50%, 80%, and 95% utilization.
   - Expect wait to climb steeply near saturation; report the three numbers.
8. Version-replay drill: write ten fake prediction log lines with model version
   and latency, then replay the incident window filtering by version.
   - Expect two clean groups (old vs new version) with separate p50/p99.
9. Shadow-compare harness: score the same ten inputs with two fake model
   versions and print per-input agreement plus distribution shift.
   - Decide in writing whether you would promote; cite error and latency bands.
10. Contract-break test: send five requests with extra fields, missing fields,
    and wrong units at a validating gateway stub.
    - Expect explicit accept/reject per versioned contract, never silent guessing.
11. Replay a mixed-version incident: interleave twenty fake log lines from two
    versions, then compute p50/p99 per version and name which one regressed.
    - Expect the regressed version isolated cleanly; report both pairs.
12. Build a per-leg budget table from a 200 ms p99 cap: split preprocessing,
    model, postprocess, and network, then justify each share in one line.
    - Verify the shares sum to the cap and name which leg gets cut first.
13. Write a rollback drill script: flip routing back, confirm prior version warm,
    and print the time from decision to restored p99.
    - Expect routing-only rollback with no artifact rebuild step.
14. Size replicas from peak load: given peak requests per second and measured
    per-replica throughput, compute replica count plus headroom.
    - Show the headroom fraction explicitly; state the queue-depth warning level.

## Submission check
- All programs compile with `javac --release 21 -encoding UTF-8` and print pure ASCII.
