# Architecture - Causal Mini-Toolkit

JDK-only layout (package com causallab):

```
CellTable   - treatment x stratum counts; pooled rates on demand
Stratifier  - within-stratum gaps + population-weighted adjustment
DiDEngine   - double difference from 2x2 group-period means
Balance     - covariate mean gaps per stratum (matching diagnostics)
Sensitivity - re-runs adjustment under shifted weights
```

## Data flow

Counts -> CellTable -> Stratifier (adjusted gap) and Balance (did it
work?) -> Sensitivity (how fragile?). Time data instead flows into
DiDEngine with pre-trend plots attached, not hidden.

## Design choices

- Counts stored as long, rates computed as double on read - no float
  drift in the raw evidence.
- Every estimator returns a record {estimate, assumption-string} so the
  license travels with the number and cannot be dropped downstream.
- Balance refuses to print an adjusted number when within-stratum
  imbalance exceeds a set tolerance; fix the match first.

## Boundaries

No causal discovery or graph search lives here: structure comes from
subject matter, entered explicitly. The toolkit computes under stated
assumptions; choosing them stays human work.

## Record sketches

```java
record Estimate(double value, String assumption) {}
record Stratum(long treatedN, long treatedX, long controlN, long controlX) {}
```

Estimate binds number to license at the type level; Stratum keeps counts
as longs until rate computation so no float drift enters the evidence.

## Failure routing

Empty strata throw with the stratum name; zero denominators never yield
NaN - they yield an exception explaining which cell is empty and why the
design cannot answer there.
