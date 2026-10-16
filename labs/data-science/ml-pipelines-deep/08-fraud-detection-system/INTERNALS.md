# Fraud Detection System - Internals

## Imbalance metrics
- With tp=80, fp=120, fn=20: precision 0.400, recall 0.800, F1 0.533.
- Precision answers reviewer load; recall answers missed fraud; F1 is their harmonic mean.
- Never tune on accuracy here; it rewards the trivial always-legitimate classifier.

## Cost tradeoff
- Expected cost per window: misses * costPerMiss + reviews * costPerReview.
- With an illustrative 10:1 ratio the middle threshold costs 320 versus 350 and 440 at the extremes.
- Real ratios come from business review, not from this lab; the method transfers, the numbers do not.

## Label lag
- The snippet curve (5% day 0 rising to 100% day 6) shows why fresh windows understate fraud.
- Metrics on immature windows are provisional; promotion uses mature windows.
- Join labels by stable transaction key; recompute metrics as labels land.

## Hybrid mechanics
- Rules short-circuit known patterns before model scoring to save latency.
- Review-band width sets queue depth; monitor precision inside the band separately.
- Adversarial shifts first appear as rule-hit decay and score-mix movement.

## Metric arithmetic
- From tp 80, fp 120, fn 20: P = 80/200 = 0.400, R = 80/100 = 0.800.
- F1 = 2 * 0.4 * 0.8 / 1.2 = 0.533, the harmonic mean punishing imbalance.
- Raising fp to 240 drops precision toward 0.25 while recall holds: reviewers pay.

## Cost structure
- Each threshold sets FN and FP counts; cost prices the pair, not the rate.
- The middle wins at 320 because it balances misses against reviews at 10:1.
- Refitting the ratio to 5:1 can move the minimum; the method, not the answer, is the lesson.

## Maturity mechanics
- Observed fraud at age d equals true fraud times labeled-fraction(d).
- The snippet curve from 5% to full near day 6 multiplies early recall down hard.
- A 90%-labeled gate admits only days past the bar into official metrics.

## Band precision
- Precision inside the review band differs from overall precision; track both.
- Band width sets queue inflow; inflow against staffing sets stability.
- Ordering by score concentrates fraud at the top reviewers read first.

## Shift signatures
- Rule-hit decay with steady volume means attackers moved, not traffic.
- Score-mix movement without rule change means the model sees novelty.
- Both together trigger the emergency-rule path before any retraining.
