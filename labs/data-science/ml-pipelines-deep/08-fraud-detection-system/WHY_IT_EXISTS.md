# Fraud Detection System - Why It Exists

Fraud is rare, costly, adversarial, and time-sensitive. Those four properties together defeat generic classification setups tuned on accuracy.

The hybrid exists because no single layer covers everything: rules react today, models generalize, reviewers resolve ambiguity and create labels.

Latency budgets exist because a perfect score after the money moves is worthless; slow signals must stay out of the request path.

Mature-window evaluation exists because labels arrive late; grading fresh traffic pretends otherwise and misleads every decision built on it.

Rules exist because attack response cannot wait for retraining. A deployed rule blocks tonight; a retrained model ships next week.

Review queues exist because the middle band is genuinely ambiguous. Human labels there are both risk control and future training data.

Cost framing exists because precision and recall alone do not price mistakes. Misses and reviews carry different costs that the threshold must balance.

Refresh cycles exist because attackers adapt. Static defenses decay even when data pipelines run perfectly.

## Why each layer exists

Rules exist as the same-day immune response: a new attack pattern gets a deterministic
block within hours while the model pipeline needs mature labels and a full retrain.
Speed here is not impatience; it is the only cover available before the next wave.

The model exists for the traffic rules cannot name: novel combinations, shifted
ranges, and patterns too diffuse for deterministic text. Generalization covers the
gap between yesterday's signatures and tomorrow's retrain, priced by the cost math.

Reviewers exist where ambiguity is genuine: middle-band scores that automation cannot
resolve without unacceptable error either way. Their labels do double duty as risk
control today and training data tomorrow, once reconciled against mature disputes.

Mature windows exist because haste lies: grading fresh traffic with sparse labels
understates fraud and rewards models that look calm while missing everything. The
day-6 curve is not bureaucracy; it is the earliest honest report available.

## What the system refuses to do

The system refuses accuracy as a metric: at order-of-magnitude skew it crowns the
always-legitimate classifier and ships a detector that detects nothing. Precision,
recall, and cost at the operating point replace it without exception.

The system refuses slow features in the request path: multi-hop lookups and long
aggregates ride async precompute with documented defaults, never blocking waits.
A perfect score after the funds move protects nobody.

The system refuses caller-visible internals: thresholds, rule text, and band edges
stay in audited logs while responses stay generic. Every revealed detail is free
attacker tooling for probe tuning.

Cost framing exists as the honest accountant: precision and recall describe the
tradeoff, but only priced misses against priced reviews pick the threshold. The
ratio comes from the organization owning the losses, never from a lab notebook.
