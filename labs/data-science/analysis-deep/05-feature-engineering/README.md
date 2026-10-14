# Lab 05 - Feature Engineering

Turning raw columns into model-ready numbers: encodings, scalings,
transforms, and interactions - with the leakage discipline that keeps them
honest.

## What you will learn

- Choose one-hot vs ordinal vs target encoding, and state what each claims.
- Scale with min-max, z-score, or robust (median/IQR) formulas by hand.
- Apply log transforms to right skew and build interaction terms.
- Fit every parameter on train only; transform test and folds with the
  frozen values.
- Describe target-encoding leakage and the hashing trick without libraries.

## Working data

- Colors {red, blue, green, red} one-hot encoded against [red, green, blue].
- Scale demo {10, 20, 30, 40, 50}: pop sd 14.142135623730951, min-max
  [0, 0.25, 0.5, 0.75, 1.0], z [-1.414, -0.707, 0, 0.707, 1.414], robust
  [-1.0, -0.5, 0.0, 0.5, 1.0].
- Train {10,20,30,40} (mean 25.0, sd 11.180339887498949) vs test {25, 100}:
  z 0.0 and 6.7082039324993685; leaky all-data mean 37.5 shown as warning.
- Housing rows: area x rooms interactions 100/240/480 with log-areas
  3.912023005428146, 4.382026634673881, 4.787491742782046.

## Build and run (plain JDK only)

```text
javac --release 21 -encoding UTF-8 FeatOneHot.java
java FeatOneHot
```

Only `java.util` and `java.lang.Math`. Matrices are printed arrays; nothing
is hidden inside a library call.

## Suggested path

THEORY.md for encoding/scaling/transform rules, CODE_DEEP_DIVE.md for the
three verified programs, STEP_BY_STEP.md to check each number by hand, then
EXERCISES.md. Keep COMMON_MISTAKES.md open: leakage mistakes look correct
until the leaderboard (or audit) disagrees.
