# Debugging - Anomaly Detection

## 1. No flags on obviously bad data

Cause: fitting the Window on data containing the incidents (new normal
fallacy) or z masked by extremes. Fix: exclude incident periods from
history; cross-check with IQR/robust-z.

## 2. Everything flags after a deploy

Cause: bulk shift (new sensor scale, renamed event) against a stale
Window. Fix: compare pre/post center/spread, re-fit, re-sweep - and add
a distribution-drift alert on the inputs themselves.

## 3. PPV math disagrees with observed precision

Cause: prevalence estimated on the wrong population (labeled sample
enriched vs production). Fix: prevalence must come from production
volumes; recompute Bayes with that number and reconcile.

## 4. Threshold sweep looks flat (P stuck)

Cause: scores tied (quantized feature) or labels leaked into scores.
Fix: check score distinctness; verify labels played no role in scoring
before the sweep.

## 5. IQR flags a whole skewed tail

Cause: lognormal-ish data against symmetric fences. Fix: transform
(log) first or set one-sided fences with the asymmetry documented.

## 6. Integer-division rates in P/R

Symptom: P/R print as 0.000 or 1.000 only. Cause: int/int division.
Fix: cast to double before dividing (all snippets do this visibly).

## 7. Outcome log contradicts the curve

Cause: reviewers grade differently than label definitions (borderline
cases). Fix: publish grading rubric with examples; measure inter-rater
agreement before trusting precision-at-k.

## 8. Score distribution collapse

Symptom: all scores identical (sweep table flat). Cause: constant feature
or saturated normalization mapping everything to one bin. Fix: check
feature variance upstream; re-scale on the clean Window, not globally.
