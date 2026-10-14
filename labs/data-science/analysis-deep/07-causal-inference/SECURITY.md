# Security Notes - Causal Inference

## Trial integrity

Randomization lists, allocation concealment, and pre-registered
outcomes are security controls: leaked assignments enable gaming,
switched outcomes enable p-hacking. Guard them like credentials.

## Re-identification via strata

Fine strata (rare disease + small clinic + age band) isolate
individuals. Coarsen public tables, suppress small cells, and keep
unit-level potential-outcome tables off shared drives.

## Instrument and cutoff gaming

Published cutoffs invite score manipulation; published instruments
invite strategic response (clinics relocating, applicants retaking).
Monitor density around thresholds and treat bunching as a breach of
the design, not a data quirk.

## Causal claims as attack surface

A "proven effect" moves markets, prescriptions, and policy - which
makes analyses targets for cherry-picking pressure. Versioned analysis
plans and immutable logs of specification changes are the defense.

## Code-level hygiene (JDK)

No network or file I/O in this lab's snippets. Keep counts as long
until rate computation, cast before dividing, and fail on empty strata
rather than dividing by zero into a plausible-looking lie.

## Coerced analysis pressure

Stakeholders who need a result can pressure subgroup selection until it
appears. Immutable analysis plans plus logged specification changes make
coercion visible - process as a shield for the analyst.

## Data-linkage leakage

Merging trial data with external records for "richer covariates" can
re-identify participants and import post-treatment variables. Review
every linkage for both privacy and collider risk before joining.
