# Visual Guide - Experimentation

## 1. The readout card

One card: d with 95% CI as a dot-and-whisker, n per arm, MDE marker,
SRM status lamp. If the whisker crosses zero, the card says so loudly -
no squinting at p-values required.

## 2. CI vs threshold sketch

Number line with the CI whisker and a vertical ship-threshold line.
Ship only when the whole whisker clears the line; overlapping means
"compatible with too-small," however significant.

## 3. Power curve

MDE on y vs n on x (log-x), annotated at the SampleSize points
(1000 -> 0.0376 ... 64000 -> 0.0047). The flattening curve teaches the
4x-for-half lesson better than algebra.

## 4. Peeking fan

Simulated null trajectories of z across six peeks with +/-1.96 lines;
highlight paths crossing at least once (~26% at independence). One
picture ends most peeking debates.

## 5. SRM bar pair

Two bars (observed counts) with expected line across; flagged splits
show the visible lean (5400/4600) next to the calm pair (5050/4950).

## 6. Novelty decay

Weekly effect points trending to flat; shade week 1 as the novelty
zone. Decisions drawn from the flat tail, never from the shaded spike.

## 7. Horizon calendar strip

Calendar bar marking launch, weekly-cycle coverage, and readout date,
with peek attempts (if any) flagged in red. The strip makes horizon
discipline visible to stakeholders who never read the stats section.

## 8. Decision matrix board

Grid of past tests: rows hypotheses, columns outcome (ship/kill/null),
cells colored by decision with MDE noted. Patterns emerge - "onboarding
nudges never clear 0.5pp" - that no single readout shows.
