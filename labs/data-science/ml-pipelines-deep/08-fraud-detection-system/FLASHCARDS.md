# Fraud Detection System - Flashcards

Q: Why not accuracy? A: Skew rewards always-legitimate; use precision/recall.
Q: Precision vs recall here? A: Flag correctness vs fraud coverage.
Q: F1 formula? A: 2PR/(P+R); 0.533 in the worked example.
Q: Expected-cost formula? A: FN*cFN + FP*cFP per window.
Q: Cost ratio in the snippet? A: Illustrative 10:1, not a real loss figure.
Q: Where do slow features live? A: Async precompute, out of the request path.
Q: Rules vs model split? A: Rules for known patterns; model for the rest.
Q: Review band? A: Uncertain scores queued for manual labels.
Q: Why mature windows? A: Labels arrive late; fresh windows understate fraud.
Q: Maturity example? A: 5% labeled day 0, full coverage around day 6.
Q: Adversarial adaptation? A: Attackers shift behavior after blocks.
Q: Queue overflow lever? A: Threshold, ordering, staffing, emergency rules.
Q: Train/serve skew check? A: Compare logged serving vs training features.
Q: Never reveal what? A: Thresholds and rule internals to callers.
Q: Fallback on timeout? A: Safe default plus alert, never unbounded wait.
Q: Operating point definition? A: Threshold minimizing expected cost within capacity.
Q: Cost formula terms? A: Misses times miss-cost plus reviews times review-cost.
Q: Snippet cost numbers? A: 320 middle vs 350 and 440 at extremes, illustrative 10:1.
Q: Threshold down effects? A: TP and FP both rise; precision either way.
Q: PR curve why? A: Summarizes all thresholds, not one point.
Q: Inline budget covers? A: Amount, velocity, rules, warmed model.
Q: Async default rule? A: Documented safe value, never a blocking wait.
Q: Feature parity test? A: Overlap join of serving vs training values.
Q: Emergency rule role? A: Same-day cover while the model retrains.
Q: Rule expiry? A: Narrow scope, expires unless renewed.
Q: Queue ordering key? A: Score plus value at risk.
Q: Queue overflow options? A: Tighten band, order by risk, staff, emergency rules.
Q: Time-to-decision why? A: Stale reviews lose blocking value.
Q: Maturity ages? A: 5% day 0 to full around day 6 in the snippet.
Q: Equal-maturity rule? A: Compare windows only at the same label age.
Q: Rule-hit decay means? A: Attackers shifted; refresh cycle due.
Q: Score-mix movement means? A: Pattern change; investigate before retraining.
Q: Reviewer precision? A: Review labels vs mature dispute outcomes.
Q: Probing pattern? A: Many near-identical low-value attempts, one source.
Q: Generic responses why? A: Exact thresholds help attackers tune probes.
Q: Fallback alert? A: Every safe default pages; survival is not operation.
