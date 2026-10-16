# Fraud Detection System - History

## Shared background
- Martin Kleppmann, Designing Data-Intensive Applications (O'Reilly, 2017), systematized batch versus stream processing and log-based data integration used across these labs.
- Sculley, Holt, Golovin and colleagues, "Hidden Technical Debt in Machine Learning Systems" (NIPS 2015), documented how serving, glue code, pipelines, and monitoring dominate production ML cost.
- Breck and colleagues' ML Test Score rubric extended that line of work into scored production-readiness checks for data, models, and infrastructure.

## Detection specifics
- Precision/recall operating-point analysis comes from information retrieval and detection theory, built for skewed classes where accuracy misleads.
- Cost-based thresholding follows decision-theoretic practice: weigh error types by consequence, not by count symmetry.
- Rules-plus-model hybrids with human review queues come from operational risk practice, pairing automation speed with judgment on ambiguity.
- Chargeback and dispute driven label delay is a long-standing payments-industry property, forcing mature-window evaluation.
- Adversarial adaptation framing follows security practice: defenses that work change attacker behavior, requiring refresh cycles.
- IR-operating-point deepened: precision/recall analysis grew where classes
  skew and retrieval sets dwarf relevant documents — the same arithmetic
  shape as fraud traffic. The snippet triple (P 0.400, R 0.800, F1 0.533
  from tp 80, fp 120, fn 20) is that analysis executed on illustrative
  counts, with accuracy discarded for rewarding the trivial classifier.
- Decision-theory deepened: thresholding by expected cost weighs error
  types by consequence, so the 10:1 illustrative ratio moves the minimum
  to the middle threshold at 320 versus 350 and 440. The method — price
  misses against reviews, minimize within capacity — transfers while the
  ratio itself stays organizational, never lab-supplied.
- Ops-risk deepened: pairing automation speed with human judgment on
  ambiguity is the review-queue pattern — uncertain bands queue ordered
  by score and value, and reviewer labels become both risk control and
  future training data when reconciled against mature disputes.
- Payments-delay deepened: dispute-driven label arrival over days forces
  the maturity curve (5% day 0 toward full near day 6), so official
  metrics wait for joined ground truth and fresh windows stay
  provisional; grading early flatters haste and punishes care.
- Security-practice deepened: defenses that work reshape attacker
  behavior, which is why rule-hit decay and score-mix movement are
  leading signals rather than lagging ones. Refresh cycles for rules,
  thresholds, and features are the budgeted answer to adaptation.
- Latency-budget deepened: request-path economics force the inline/async
  split — cheap features, rules, and the warmed model inside the budget,
  slow lookups precomputed outside it. A perfect score after funds move
  protects nothing, so timeouts fall back to safe defaults with alerts.
