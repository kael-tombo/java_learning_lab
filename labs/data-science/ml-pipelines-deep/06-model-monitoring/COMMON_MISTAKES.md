# Model Monitoring - Common Mistakes

1. Treating a drift number as a universal pass/fail line instead of a tracked signal.
   - Fix: trend it per feature; page only on validated high-precision rules.
2. Computing quality on fresh, immature labels and reacting to phantom drops.
   - Fix: restrict official metrics to mature windows; mark the rest provisional.
3. Watching only aggregates while a key slice breaks unnoticed.
   - Fix: track per-segment metrics for every segment that matters.
4. Paging on low-precision alerts until on-call ignores them.
   - Fix: cut paging rules to the few worth waking for; dashboard the rest.
5. Alerts without runbook links, so every page starts from zero.
   - Fix: every page names slice, signal, and first triage steps.
6. Letting reference windows drift silently instead of refreshing them deliberately.
   - Fix: pin references; refresh by review with a recorded reason.
7. Monitoring values but not telemetry presence, missing silent outages.
   - Fix: alert on missing data volume as well as on bad values.
8. Feeding model-influenced outcomes back into training without accounting for the loop.
    - Fix: label the loop explicitly and validate retraining sources.
9. Comparing windows of different maturity and calling the gap a regression.
    - Fix: compare only equal-maturity windows; annotate maturity on every chart.
10. Using one global threshold across slices with different base rates.
    - Fix: fit thresholds per slice or normalize before comparing.
11. Refreshing references silently after every incident, normalizing decay.
    - Fix: require reviewed reason and owner sign-off for each refresh.
12. Tracking means of skewed scores instead of the mix and tail behavior.
    - Fix: watch score distribution shape plus positive rate, not a single mean.
13. Keeping every experimental monitor paging after the experiment ends.
    - Fix: expire trial rules by date; promote to paging only on proven precision.
14. Recomputing reference statistics on every run instead of pinning them.
    - Fix: compute once, store with the snapshot, reuse until reviewed refresh.
15. Ignoring seasonality and paging on calendar effects every cycle.
    - Fix: compare against the same season's reference or deseasonalize first.
   - Fix: label the loop explicitly and validate retraining sources.

## Review habit
- Monthly: check alert precision, reference freshness, and slice coverage together.
- Quarterly: retire monitors whose precision decayed below the paging bar.
