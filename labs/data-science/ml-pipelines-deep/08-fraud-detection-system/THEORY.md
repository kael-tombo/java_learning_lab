# Fraud Detection System - Theory

Fraud detection flags a small minority of abusive events quickly enough to act, without blocking legitimate users.

## Imbalance framing
- Fraudulent events are an order of magnitude rarer than legitimate ones, typically far below 1% of traffic.
- Accuracy is uninformative at that skew: always predicting legitimate scores well above 99% while catching nothing.
- Report precision (fraction of flags that are fraud) and recall (fraction of fraud flagged), plus review capacity.

## Operating point
- The score threshold sets the tradeoff: lower thresholds raise recall and review load; higher thresholds cut reviews but miss more fraud.
- The threshold is picked from cost asymmetry: a missed fraud generally costs more than one manual review, stated qualitatively since real figures vary.
- Expected cost per window is misses * costPerMiss + reviews * costPerReview; the minimum over thresholds is the operating point.

## Features under latency
- Inline features must answer inside the request budget: amount, velocity counters, device and session attributes.
- Slow features (multi-hop graph lookups, long aggregates) stay out of the request path and serve through precomputed stores or async updates.
- Feature logging must match serving values exactly; train/serve skew here directly becomes missed fraud.

## Hybrid shape
- Deterministic rules block or step up known-bad patterns immediately and are cheap to update during an attack.
- The model scores the remaining traffic; scores in an uncertain band go to manual review queues.
- Reviews produce labels that retrain the model and refine rules, closing the loop.

## Delay and adversaries
- True labels arrive late because disputes and chargebacks take days, so evaluation uses mature windows.
- Adversarial adaptation means attackers change patterns once blocked; feature distributions and rule hit rates need refresh cycles.
- Track rule hit rate, model score mix, review precision, and time-to-label as leading health signals.
