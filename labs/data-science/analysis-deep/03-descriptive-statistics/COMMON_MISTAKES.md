# Descriptive Statistics - Common Mistakes

## 1. Quoting variance without its divisor

"Variance 30.8" vs "variance 36.0" differ by which question was answered.
Always label pop (n) or sample (n - 1); the lab prints both for this reason.

## 2. Leading with the mean on skewed data

Reporting 10.57 alone as "typical" overstates half the cases. Lead with
median 9.0 + IQR 6.5 when mean and median visibly disagree.

## 3. Reading causality into r = 0.99

The demo pair correlates nearly perfectly by construction; correlation never
carries direction. State association, then demand design (experiment, time
order, controls) for causal talk.

## 4. Trusting moments on dirty data

One miscoded 210 sends skew past 2 and sd soaring while median sits at 9.0.
Clean (or at least fence-check) before moment interpretation.

## 5. Forgetting the zero-spread branch

Constant columns make r undefined (0/0), not zero. Ship the explicit guard;
a NaN with a message beats a NaN that propagates silently.

## 6. One-pass variance on large means

sum(x^2) - n*mean^2 cancels catastrophically when means dwarf spreads.
Default to two-pass (mean, then deviations) unless a tested online algorithm
is in place.

## 7. Sorting the caller's array

Median via in-place sort mutates shared state and surprises callers. Clone
before `Arrays.sort`, as the snippets do.

## 8. Mode ties reported as fact

Two values tied at top frequency is "bimodal", not "mode = first found".
Report ties; the argmax shortcut is a display convenience, not a finding.

## 9. Kurtosis read as peakedness only

Excess kurtosis blends peak and tails; -0.62 here mostly says tails are
mild. Pair it with quartiles before claiming anything about the center.

## 10. Dropping n from the report

r = 0.99 on n = 5 is suggestive, not conclusive. Every summary ships with
its n (7 here, 5 for the pair), or readers cannot calibrate belief.
