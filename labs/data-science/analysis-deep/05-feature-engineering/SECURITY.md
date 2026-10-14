# Feature Engineering - Security Notes

## Target means as data disclosure

Per-level mean outcomes are statistics about groups: rare levels (k = 2)
leak near-individual outcomes. Suppress or heavily smooth small-k levels
before exposing encodings, models, or explanations externally.

## Vocabulary as roster

A shipped vocabulary lists every level seen in train - customer names,
diagnoses, locations. Treat vocabularies as sensitive artifacts: hash or
prune rare levels, restrict circulation like the training roster itself.

## Poisoning via fit inputs

Attackers who influence train rows shift means, bounds, and target encodings
(min-max is one extreme away from capture). Bound influence: robust scaling,
rare-level collapsing, smoothing weight m, and outlier review before fit.

## Unknown-level handling as availability

A feed drifting to 90% unknown levels degrades the model silently if the
fallback is quiet. Alert on unknown-rate spikes; fallbacks keep serving, but
humans must hear about the drift.

## Reproducibility of fitted constants

Parameter objects (mean 25.0, sd 11.180339887498949, vocab order, shift c)
belong in versioned artifacts beside the model: any silent change redefines
features and voids validation. Hash and pin them.

## No raw labels in transform logs

Target-encoding diagnostics must quote smoothed, aggregated values with k
attached - never row-level labels. Debug the formula on synthetic levels
(like A 2/10, B 40/50), not on real outcomes.

## Availability under drift

A feed whose vocabulary churns 50% overnight turns the unknown fallback into
the main path: accuracy decays while uptime stays green. Track fallback and
out-of-range rates as first-class health metrics with paging thresholds, not
curiosity dashboards - silent degradation is still an outage to users.
