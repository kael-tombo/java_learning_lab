# ML Pipelines Deep — Real-World Project: Fraud-Scoring Service Slice

Build a latency-bounded scoring service for a synthetic transaction
stream: feature computation with event-time semantics, a trained
binary classifier behind a millisecond-scale budget, threshold tuned
on validation for a stated precision/recall operating point, and a
monitoring loop tracking prediction distribution plus a delayed-label
accuracy backfill.

Acceptance: p99 scoring latency under the stated budget at the target
rate; a canary slice of traffic scored by challenger vs champion with
the comparison logged; a drift dashboard showing prediction-rate time
series with alert rules that reference runbook actions; a quarterly
retrain procedure (new snapshot → gated train → locked-test evaluation
→ staged promotion) executed at least once end to end. Synthetic data
is expected — the graded artifact is the machinery (lineage, gates,
alerts, rollback path), exercised honestly, not the model quality.
