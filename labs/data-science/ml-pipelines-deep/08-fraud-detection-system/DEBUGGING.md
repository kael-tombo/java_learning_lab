# Fraud Detection System - Debugging

## Legitimate users blocked
- Cause: threshold too aggressive or a rule too broad after an incident.
- Check: review precision and rule-hit breakdown for blocked traffic.
- Fix: narrow the rule; move the threshold using cost math and review capacity.

## Fraud spike missed
- Cause: new pattern outside rules and shifted feature range.
- Check: score mix movement and rule-hit decay over the window.
- Fix: emergency rule for cover, then retrain on mature labels.

## Metrics disagree across dashboards
- Cause: one side uses provisional labels, the other mature windows.
- Check: label-maturity age behind each metric.
- Fix: standardize on equal-maturity windows for comparison.

## Review queue overflows
- Cause: threshold lowered without staffing cover, or attack burst.
- Check: flag rate versus decisions per hour.
- Fix: tighten band temporarily; order by score and value at risk.

## Train/serve skew
- Cause: feature logged differently in training and serving paths.
- Check: join logged serving features against training values for overlap traffic.
- Fix: single shared feature code path; pin it in lineage.

## Score mix drifts, rules quiet
- Cause: slow adversarial shift the rules were never written for.
- Check: score distribution movement against rule-hit trends.
- Fix: narrow emergency rule now; retrain on mature labels next.

## Review precision collapses
- Cause: band widened without capacity math, or attack burst flooding.
- Check: band precision versus overall precision over the window.
- Fix: tighten the band; order by risk; staff or rule-cover the burst.

## Safe defaults dominate
- Cause: feature outage or timeout storm forcing fallback decisions.
- Check: fallback rate per feature source over the incident window.
- Fix: repair the source; defaults stay survival-only with alerts attached.

## Reviewer-model disagreement spikes
- Cause: stale reviewer guidance or shifted fraud pattern both sides misread.
- Check: reviewer precision against mature dispute outcomes per cohort.
- Fix: refresh guidance; reconcile labels before the next retraining round.
