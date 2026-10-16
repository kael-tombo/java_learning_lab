# Model Monitoring - Why It Exists

Models decay after launch: inputs shift, relationships change, pipelines break. Training metrics cannot see any of that.

Monitoring exists to translate production behavior into decisions: keep serving, roll back, retrain, or fix the pipeline. Without it, regressions surface as user complaints weeks late.

Label delay forces the issue further: true quality is unknowable at first, so provisional tracking plus mature-window evaluation is the only honest accounting.

Alerts with runbooks exist because detection without response is trivia; precision matters because ignored monitors protect nothing.

Distribution checks exist because raw accuracy hides the early signs. Score mix and feature shifts move weeks before labeled quality confirms the damage.

Slice tracking exists because aggregates lie by averaging. A model can be fine overall and broken for exactly the users who complain loudest.

Reference windows exist to anchor comparisons. Without a pinned baseline, every window looks normal relative to the last one.

Incident records exist so each outage teaches permanently: new pinned cases, retuned alerts, refreshed references.

## Why each piece exists

Provisional marking exists because fresh numbers seduce: a dashboard without maturity
marks presents guesses with the same ink as facts, and readers cannot tell which is
which. The mark restores the distinction at the point of reading, where it matters.

Pinned references exist because floating baselines forgive everything: compare each
window to the last and decay reads as stability all the way down. A pinned snapshot
with a recorded reason makes movement visible instead of negotiable.

Runbook links exist because diagnosis under paging pressure degrades: the engineer
woken at night gets slice, signal, maturity age, and first steps rendered together.
Every page without that bundle starts from zero and bills the incident for it.

Slice monitors exist because user complaints arrive pre-sliced: no one reports that
the global average feels wrong. Per-segment metrics meet the complaint where it
lives instead of answering a question nobody asked.

## What monitoring refuses to do

Monitoring refuses to grade fresh windows officially: labels have not arrived, so
the numbers are orientation, not verdicts. Official metrics wait for maturity;
everything else wears the provisional mark without exception.

Monitoring refuses universal drift cutoffs: binning, sample size, and feature
importance move every value's meaning, so trends and validated rules replace fixed
lines. A number without its binning and window is not a measurement.

Monitoring refuses silent reference refreshes: each new baseline carries a reason
and an owner, reviewable after the fact. Convenience refreshes are how decay gets
normalized one unlogged step at a time.

Monitoring refuses loop-blind retraining: labels shaped by the model's own decisions
re-enter as ground truth unless quarantined, so sources are validated before every
round. The loop is named, measured, and gated — never assumed away.
