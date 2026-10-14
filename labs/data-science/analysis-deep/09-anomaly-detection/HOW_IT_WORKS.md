# How Anomaly Detection Works

## 1. Define the event and its cost

Fraud dollar, outage minute, defect escape - with the cost of a miss
vs a false page. Without costs there is no threshold choice, only
vibes. Write both costs down first.

## 2. Baseline with z and IQR

Score history both ways (AnomBase pattern). Agreement between the two
means an obvious outlier; disagreement (z silent, IQR loud) hints at
masking or skew - investigate the shape before escalating methods.

## 3. Add the isolation view

Run the conceptual isolation check: which points separate in few
random splits? Use it to catch joint anomalies (odd combinations) that
univariate fences miss. Keep it as a second opinion, not a replacement.

## 4. Sweep the threshold

Score labeled history, sweep thresholds, record the P/R table (PrCurve
pattern). Present the curve to stakeholders and let costs pick the
operating point - the analyst's job is the curve, the business's the
point.

## 5. Confront the base rate

Plug prevalence, sens, fpr into the Bayes formula and quote PPV plus
alerts-per-day at current volumes. If PPV is 9%, say "nine of ten pages
are false" out loud before launch - then design tiers accordingly.

## 6. Tier the response

Critical tier pages humans; medium tier batches for review; low tier
feeds auto-remediation or logging. Every tier gets an outcome log so
precision is measured, not assumed.

## 7. Monitor the monitor

Track flag rate, precision-at-k reviewed, and time-to-triage weekly.
Drift in the bulk (new normal behavior) silently converts precision
into noise - re-fit baselines on a schedule, with the schedule written
down.
