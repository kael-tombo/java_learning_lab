# Mini Project: Backend Performance

## The assignment

This backend performance mini build produces a working slow-checkout performance clinic you can run locally.
Scope stays deliberately small so every backend performance behavior remains observable.
Budget roughly one focused evening for the slow-checkout performance clinic implementation.
Success means demonstrating backend performance judgment, not just compiling code.
Keep a lab journal noting each backend performance surprise encountered.
Nothing joins the work beyond what the acceptance checks already ask for.

## Parts you will wire

- Latency percentile reading.
- Connection-pool sizing.
- N+1 query detection.
- Response caching points.
- Load-generation harness.

## Build order

1. Baseline a checkout flow under a 50-user simulated load for the service.
2. Locate the slowest span with timing breakdowns.
3. Fix one N+1 access pattern in order history.
4. Size the connection pool deliberately and re-measure.
5. Cache one hot product lookup with a short TTL.

## Acceptance checks

- [ ] Baseline percentiles recorded before any change in the solution.
- [ ] Slowest span identified with evidence, not guesses in the platform.
- [ ] Order-history queries drop by at least half.
- [ ] Pool sizing rationale written with before-and-after numbers.
- [ ] Hot lookup cache hit rate exceeds half under load.

## Stretch

Grow the project by adding one realistic complication you select.
Write the two-paragraph retro: which backend performance decision proved hardest.
Give the demo to a peer whose only map is the acceptance checks.
