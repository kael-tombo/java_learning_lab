# Fraud Detection System - Why It Matters

Missed fraud is direct loss; false blocks are churn and support load. The operating point prices both explicitly instead of hiding them in accuracy.

Review capacity is the binding constraint in practice. Threshold math that ignores staffing produces queues that age out before decisions.

Latency decides coverage: signals too slow for the request path must be precomputed or they simply do not protect online traffic.

Adversarial pressure means stasis is decay. Systems without refresh cycles degrade even when nothing else changes.

Rule agility decides incident response time. Versioned rules ship cover in hours; model-only systems wait for the next train.

Label maturity decides metric honesty. Provisional grading flatters fresh models and punishes careful ones.

Logging completeness decides audit survival. Every blocked transaction needs its evidence trail: score, rules, features, version.

Hybrid design decides robustness. Each layer covers the others' blind spots: rules, model, and reviewers fail differently.

## Pricing mistakes honestly

The operating point turns two harms into one number: misses times miss-cost plus
reviews times review-cost, minimized within review capacity. The snippet ranking —
320 middle against 350 and 440 — shows balance beating extremes at the illustrative
ratio; refits move the answer but never the method.

Accuracy hides both harms at once: the trivial classifier scores above 99% while
catching nothing, and every decision built on that number misprices risk. Teams
that report precision, recall, and cost per threshold make the tradeoff auditable;
teams that report accuracy make it invisible.

## Capacity as physics

Review throughput is the binding constraint no threshold math can wish away: flag
rates above decisions-per-hour age cases out before review, converting detection
into archaeology. Bands sized from staffing keep the queue stable; bands sized
from optimism flood it on the first attack burst.

Latency is coverage physics: signals that miss the request budget do not protect
online traffic regardless of their offline quality. The inline/async split with
safe defaults is what keeps slow intelligence in the fight via precompute instead
of on the bench via timeouts.

## Adaptation as routine

Rule agility compresses incident response from retraining cycles to hours: versioned
rules ship cover tonight while models retrain on mature labels for next week. The
emergency-rule path with expiry keeps that speed without accumulating permanent
unreviewed policy.

Refresh cadence converts decay into maintenance: rule-hit decay and score-mix
movement trigger reviews on schedule, attackers shift, and the cycle repeats by
design rather than by surprise. Stasis is the only losing strategy on offer.

Logging completeness closes the loop for audit and learning: score, rule hits,
features, and version per decision let any block explain itself months later.
Systems that cannot replay a decision cannot defend it, retrain from it, or
prove it was ever correct.
