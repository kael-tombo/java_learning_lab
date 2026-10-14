# Data Wrangling - Interview Questions

## Q1. How do you decide between dropping and imputing missing values?

A: Diagnose the mechanism first. Under MCAR with a low missing rate,
deletion is honest and simple. Under MAR, impute conditional on the observed
drivers (bands, model) rather than a global fill. Under MNAR, admit the
extra assumption and preferably model the mechanism - no fill is neutral.

## Q2. What is wrong with filling NaN with zero?

A: Zero is a value, not "unknown". On `{2, 4, NaN, 8, 10}` a zero-fill gives
mean 4.8 instead of 6.0 - a fabricated loss. Rejects and gaps must stay
distinguishable from measured zeros.

## Q3. How do you dedup a 10-million-row file on the JDK?

A: Stream rows, normalize key fields (trim, case-fold), hash into a
`HashSet`/`LinkedHashMap` of keys, keep first-seen. O(n) average time, O(u)
memory for u unique keys; spill keys to disk if u exceeds memory.

## Q4. IQR flags and z-scores disagree. What now?

A: Report both and inspect skew. In right-skewed data the sd is inflated, so
z-screens under-flag while IQR flags the tail - disagreement itself
diagnoses skew/masking rather than a bug.

## Q5. Your parser rejects 30% of a column after a feed change. Walk me
through it.

A: Check the reject reasons distribution first (new sentinel? thousands
separators? encoding?). Quarantine rejects, confirm with the feed owner,
then extend the grammar explicitly - never relax parsing silently.

## Q6. How do you validate a cleaning run?

A: Row reconciliation (in = kept + removed + rejected), missing recount,
before/after mean and spread comparison, and rerun determinism. Any check
that fails blocks downstream use.

## Q7. Explain variance shrinkage to a stakeholder.

A: "Every gap filled with the average makes the data look more certain than
it is. Our error bars after filling are optimistic by design, so we widen
them / run sensitivity with median fills before deciding."

## Q8. When would you NOT remove an outlier?

A: When the flag is the phenomenon: fraud, outage, breakthrough. Remove only
proven collection errors, and even then log the removal. Default to
robust methods (median, IQR) that tolerate the point instead.
