# Architecture - Experimentation Mini-Toolkit

JDK-only layout (package com.explab):

```
Counts    - x_A, n_A, x_B, n_B with validation (x <= n, n > 0)
Readout   - d, SE, z, p, CI from one Counts object
SrmCheck  - chi-square on arm counts vs planned ratio
PowerPlan - SE/MDE table over candidate n (planning only)
Log       - append-only hypothesis/result rows
```

## Data flow

Traffic -> Counts -> SrmCheck (gate) -> Readout (d + CI) -> Log.
PowerPlan runs before launch from assumed rates, never from observed
peeks - the call graph makes peeking-driven resizing awkward by design.

## Design choices

- Counts immutable; every derived number recomputed from the four
  inputs so no stale-rate bug is possible.
- Readout returns the interval alongside p; no API yields p alone.
- SrmCheck runs on allocation counts only, blind to metrics, so the
  gate cannot be influenced by promising goals.
- Log rows include horizon and MDE to shame post-hoc reinterpretation.

## Boundaries

No sequential-testing engine here: fixed-horizon analysis only, with
sequential methods described conceptually in THEORY.md.

## Record sketches

```java
record Counts(long xA, long nA, long xB, long nB) {}
record Readout(double d, double se, double z, double p, double lo, double hi) {}
```

Counts validates x <= n at construction; Readout has no p-without-CI
projection - the interval travels with the p-value by construction.

## Failure routing

n = 0, x > n, or negative inputs throw naming the arm. SrmCheck takes
planned ratio as a required argument - no default split exists anywhere.
