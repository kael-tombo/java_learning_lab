# REAL_WORLD_PROJECT — Data Stream Algorithms
> Live trending-keys service: Misra-Gries candidates plus Count-Min estimates over a 1-minute tumbling window, audited against exact samples.

## System and inputs
- Event bus delivers (key, timestamp) at bursty rates; window service keeps MG(m=200) and CM(w=2048, d=4) per minute-window.
- 1-in-1000 sampled substream kept exactly for audit; sampler uses a fixed hash prefix so audits are reproducible.
- Top-20 keys per window published to the trends API with (mg_est, cm_est, exact_if_sampled).

## Design
- Single-pass update per event: MG decrement-or-insert, then CM row increments; O(1) work per event.
- Window close freezes structures, publishes, and resets; late events within 5 s grace join the closing window, later ones are counted as late.
- Nightly audit replays the sampled substream exactly and reports recall of the published top-20 and max CM overestimate.

## Metrics
- Per-window recall of published top-20 vs exact top-20 on the sampled substream.
- Max and p99 CM overestimate ratio (est/true) per window.
- Late-event rate and dropped-event rate (backpressure counter).
- Memory bytes per window vs the configured budget.

## Failure modes
- Cardinality explosion (key space 100x normal): MG counters churn; alert on decrement-round rate, temporarily widen m by policy.
- Hash-seed collision with an attacker-crafted key set: seeds rotate weekly; rotation is a config push, not a deploy.
- Audit sampler bias: sampler hash verified uniform on a weekly chi-square check over buckets.
- Backpressure: bounded queue (10k) then drop-with-counter; drops are dashboarded, never silent.

## Rollout
1. Shadow: run beside the existing batch trends job for one week; compare top-20 overlap.
2. Serve internal dashboards from the stream service; keep batch as fallback.
3. Promote to the public trends API after recall stays above the agreed floor for two weeks.

## Acceptance criteria
1. Reference streams reproduce the lab outputs (MG {1=4,2=1}, CM ests 5/3/3) through the service code path.
2. Audit report shows recall and max overestimate for every window of the shadow week.
3. Drop counter increments under a synthetic 10x burst with no silent loss.
4. Seed rotation changes hashes without restarting the service (config-push test).
5. Rollback returns trends API to the batch job within 5 minutes.

## Cost and contract notes
- Per-window memory budget fixed in config (MG bytes + CM bytes + sampler bytes); exceeding it pages, since memory is the product guarantee.
- Trends API: GET /top?window=... returns (key, mg_est, cm_est) triples with the window id; audit endpoint exposes recall reports.
- Backpressure drops are billed as a first-class metric in the SLO review, not buried in logs.
- Seed rotation is a config push with canary windows; no deploy needed and old seeds retained one week for replay.
