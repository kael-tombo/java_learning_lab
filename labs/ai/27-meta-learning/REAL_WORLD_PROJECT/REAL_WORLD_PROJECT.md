# Meta-Learning — Real-World Project

**Goal**: a cold-start personalization simulator: teach a shared scoring function to
adapt per user-segment from a handful of events, with explicit honesty around what
simulators cannot prove.

## Scenario (invented, safe synthetic data)

Recommendation scores for 50 synthetic users across 6 "segments" with a per-segment
interaction preference profile. A shared base scorer must adapt to a segment using only
`K in {2, 5, 10}` events; the adaptation family here is a *per-segment scalar offset*
learned with a few SGD steps.

## Build components

1. `SegmentFixture`: hand-written preference vectors; `EventSample` generator with a
   seeded LCG (deterministic).
2. `AdaptRunner`: shared scorer with per-segment offset; two loops — base scorer tuned
   across ALL segments (a crude meta phase), then inner adaptation per segment.
3. `FewShotEvaluator`: report hit-similarity with a top-1/"top-3" evaluation per segment
   at each event budget; compare against two baselines: `no-adaptation` and
   `segment-only-history` (event-mean), and print one summary table.
4. `RobustnessProbe`: label leakage check — when the event stream contains obvious
   preference keyword-dummy "clicks", does adaptation outrank history alone... a probe
   that must be run, not assumed.

## Write-up (deliverable, graded on candor)

- Under what event budget does marginal adaptation stop paying off — quote the closing
  numbers from your table.
- Two deployment risks of per-user adaptation with tiny data: overfitting to a single
  session's mood, and privacy-adjacent profiling — describe one guard each (dispatch
  uncertainty floors; user-facing transparency + opt-out tooling).
- Unverified-beyond-simulator statement must be explicit: no benchmark claim, no external
  dataset is imported, all fixture numbers are hand-written constants.

## Constraints

`javac --release 21`, deterministic seeds, ASCII stdout, under ~400 lines total; three
runs reported (K = 2, 5, 10) with dates/points normalized to "event index" rather than
any real-world timescale.
