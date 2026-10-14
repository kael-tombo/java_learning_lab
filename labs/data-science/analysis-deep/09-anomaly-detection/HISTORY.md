# History - Anomaly Detection

Only widely documented facts; uncertain details are omitted.

## Statistical roots

- Edgeworth (1887) discussed discordant observations; the outlier
  literature grew through mid-20th-century robust statistics (Tukey's
  "Exploratory Data Analysis," 1977, gave the boxplot and the 1.5*IQR
  fences used in this lab).
- Hawkins' "Identification of Outliers" (1980) consolidated the
  classical definition: an observation deviating markedly from others,
  suggesting a different mechanism.

## Fraud and intrusion

- Credit-card fraud systems (1990s onward) industrialized anomaly
  scoring: rare-event precision problems at transaction scale forced
  the Bayes/PPV thinking this lab centers.
- Intrusion detection (Denning's 1987 model onward) split misuse
  (signatures) from anomaly (deviation) detection - the tier split in
  HOW_IT_WORKS.md descends from that divide.

## Modern methods

- Random-forest-era ensemble thinking led to isolation-based scoring
  (points separable in few random splits score anomalous) - taught here
  as intuition with no theorem claims.
- One-class and density methods matured alongside, all sharing the same
  operational lesson: thresholds are cost decisions, not math outputs.

## Lesson

A century of outlier work converges on three moves: robust baselines,
cost-picked thresholds, and Bayes-checked expectations.

## Reading the lineage

Edgeworth (discordance), Tukey (resistance), Hawkins (definition),
fraud systems (precision at scale), ensembles (isolation). Each stage
moved the question from "is it odd?" to "is it worth paging?" - the
modern detector answers the second question first.

## What scale taught

Millions of events made per-point cleverness cheap and reviewer minutes
dear. The field's scarce resource shifted from CPU to attention - every
modern practice (tiers, PPV, precision-at-k) rations attention, not flops.
