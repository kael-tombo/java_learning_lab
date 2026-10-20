# Explainable AI — Real-World Project

**Goal**: an explanation-audit toolkit for a loan-similarity triage desk: Java-side
services that produce per-application score reason lists for human reviewers, with the
honest caveats printed next to the numbers.

## Scenario (fully synthetic policies)

`Applicant` record (7 hand-written numeric features such as savings-ratio, tenure-band);
a policy-style additive scorecard + a heavier "shadow" model (small 2-layer net, hand
coded). Reviewers see reason lists; the audit checks whether shadow and scorecard agree
on reason structure.

## Components

1. `PolicyScorecard`: hand-weighted additive scorer (weights typed in as constants).
2. `ShadowNet`: 7-8-1 with tanh, hand-implemented backward (finite-difference check on
   five parameter taps, print max abs error, must stay under `1e-5`).
3. `ReasonService`: top-3 reasons per application using exact Shapley enumeration over
   the 7 features (128 subsets — fine to brute-force here), plus a LIME-style local
   surrogate on the shadow model's neighborhood.
4. `DisagreementAudit`: for each of 50 seeded applications, flag rows where scorecard
   reasons and shadow reasons disagree in the top feature; print the disagreement rate
   and three flagged case sheets.

## Governance write-up (graded section)

- Report both explanation formats' gaps: distance-to-baseline wording for Shapley, local
  radius wording for LIME — one bullet each, no numeric claim about real lending.
- Phrase-level review: paste three auto-generated reason sentences and rewrite them to
  remove any causal overclaim ("declined because" -> "this application's score is mostly
  driven by").
- Regulatory-style checklist: repetition of what cannot be guaranteed (fairness of
  attributions under correlated features; counterfactual sufficiency) listed as open
  items rather than asserted.

## Deliverables

- `javac --release 21` compile; deterministic seeds; ASCII-only console sheets.
- A six-case demo log: three agreeing and three disagreeing, each with the phi and
  surrogate summaries side by side.
