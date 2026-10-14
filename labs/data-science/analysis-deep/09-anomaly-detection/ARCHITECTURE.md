# Architecture - Anomaly Mini-Toolkit

JDK-only layout (package com.anomlab):

```
Window    - clean-history slice with center/spread (mean/sd, Q1/IQR)
Scorer    - z, robust-z (median/MAD), fence checks per point
Sweep     - threshold grid producing the P/R table from labels
Bayes     - PPV/alert-volume arithmetic from prev/sens/fpr
Tiers     - page/batch/log routing by score band + outcome log
```

## Data flow

History -> Window -> Scorer (scores) -> Sweep (curve) -> Bayes (PPV at
volumes) -> Tiers (who gets woken). Outcome logs flow back into Window
selection (incidents excluded from "normal").

## Design choices

- Window is immutable once fitted; re-fit constructs a new Window so
  live scoring never sees a half-updated center.
- Sweep returns the full table, never a "best" threshold - the pick
  needs costs the toolkit does not own.
- Bayes takes measured sens/fpr plus stated prevalence; prevalence is a
  required explicit argument, never a default, to force the conversation.
- Tiers log every routing decision with score and band for audit.

## Boundaries

No clustering or deep models here: baselines plus isolation intuition
cover the lab's scope; multivariate extensions plug in as new Scorers.

## Record sketches

```java
record Window(double center, double spread, double q1, double iqr) {}
record Verdict(int tp, int fp, int fn, double threshold) {}
```

Window is immutable once fitted; Verdict carries the raw counts so P/R
are always recomputable from evidence, never from rounded intermediates.

## Failure routing

Empty history throws at Window construction (no silent NaN center).
Thresholds outside [0, 1] for score sweeps throw naming the bound.
Outcome-log write failures page - a blind detector is worse than none.
