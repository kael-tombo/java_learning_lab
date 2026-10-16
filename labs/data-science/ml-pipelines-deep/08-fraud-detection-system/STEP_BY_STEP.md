# Fraud Detection System - Step by Step

1. Split features into inline (cheap) and async (slow) sets by measured latency.
   - Anything missing its budget gets precomputed or dropped from the request path.
2. Write rules for known-bad patterns with versioned thresholds.
   - Rules give same-day cover while the model retrains.
3. Train the model on mature labeled windows, never on provisional labels.
   - Fresh windows understate fraud because disputes have not arrived.
4. Pick the threshold from cost asymmetry and review capacity, not accuracy.
   - The operating point minimizes misses times miss-cost plus reviews times review-cost.
5. Wire scoring: rules first, model next, uncertain band to review queue.
   - Order the queue by score and value so limited reviews hit the riskiest cases.
6. Log decisions with score, rule hits, features, and model version.
   - The log must replay any decision exactly for audit and debugging.
7. Join late labels by key; report official metrics on mature windows.
   - Recompute as labels land; mark fresh windows provisional throughout.
8. Refresh rules and retrain on a cadence; watch for adversarial shifts.
    - Rule-hit decay and score-mix movement are the early warnings.
9. Order the review queue by score and value; alarm on depth before overflow.
    - Arrival-ordered queues waste scarce reviews on the least risky cases.
10. Reconcile reviewer labels against mature disputes; track reviewer precision.
    - Unreconciled labels train tomorrow's blind spots into the model.
11. Ship emergency rules narrowly scoped with expiry; renew or retire explicitly.
    - Permanent emergencies are unreviewed policy wearing an incident's clothes.
12. Watch rule-hit decay and score mix as the leading adversarial signals.
    - Labeled metrics confirm late; leading signals trigger cover early.
13. Verify feature parity by joining serving logs against training values regularly.
    - Divergence found in a join is an incident prevented; in production, a miss.
14. Drill threshold moves, queue floods, and kill-switch use on staging quarterly.
    - Each drill ends with a versioned change or a confirmed standing order.

## Launch checklist
- Inline budget met, rules versioned, threshold priced, queue staffed, labels mature.
- Parity joined, trails complete, fallbacks alerting, refresh cadence owned.
- Adversarial drill passed; emergency path authorized with expiry rules set.
- A missing item blocks launch; provisional operation needs an owner and a date.
   - Rule-hit decay and score-mix movement are the early warnings.

## Done when
- Decisions fit the latency budget, the queue is stable, and metrics use mature labels.
