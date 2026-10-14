# Experimentation Theory

## 1. Anatomy of an A/B test

- Hypothesis: a falsifiable sentence ("one-click checkout raises
  purchase rate") fixed before launch.
- Randomization unit: the entity assigned (user, session, cluster).
  Analysis should respect it - randomizing by user but analyzing by
  pageview understates variance.
- Control vs treatment: identical except the change under test.
- Goal metrics: the few numbers that decide ship/no-ship.
- Guardrail metrics: health numbers (crashes, latency, refunds) that
  can veto a win on goals.

## 2. Reading a result

Difference d = p_B - p_A with standard error
SE = sqrt(p_A(1-p_A)/n_A + p_B(1-p_B)/n_B). The z-statistic d/SE gives a
p-value; the 95% interval d +/- 1.96*SE shows the compatible range.
CODE_DEEP_DIVE.md verifies one: diff 0.01200, SE 0.00469, z 2.557,
p 0.01055, CI [0.00280, 0.02120] - significant at 0.05, barely.

## 3. Power and sample size

Power is the chance of detecting a true effect. Qualitative rules:

- Bigger true effect -> smaller n needed (effect sits in the
  denominator squared).
- SE shrinks as 1/sqrt(n): quadrupling n halves the error bar, so the
  minimum detectable effect (MDE) roughly halves too (SampleSize demo).
- 80% power at 5% significance is the common planning convention.

Plan n from the smallest effect worth shipping, not from the effect
you hope for - hoping is how underpowered tests are born.

## 4. Peeking and p-hacking

Checking daily and stopping at the first p < 0.05 manufactures false
positives: repeated looks multiply the chance that noise once crosses
the line. Remedies: a fixed horizon decided upfront (no early stops),
or sequential methods with adjusted boundaries. Trying many metrics or
subgroups until one shines is the same offense in disguise.

## 5. SRM: sample-ratio mismatch

A 50/50 split should yield ~equal arms. Systematic imbalance (broken
redirect, bot filter firing on one arm) invalidates the test even when
metrics look fine. The chi-square check sum (O-E)^2/E on arm counts
catches it; p < 0.01 conventionally flags. Verified demo in code.

## 6. Novelty and primacy

New interfaces get curiosity clicks (novelty inflates early treatment)
while entrenched habits favor the familiar (primacy). Both fade. Run
long enough to outlast them, or segment by exposure cohort and require
the effect to persist in veterans, not just newcomers.
