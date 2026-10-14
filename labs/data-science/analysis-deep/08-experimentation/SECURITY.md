# Security Notes - Experimentation

## Assignment integrity

Bucketing logic is a trust boundary: predictable hashes let users or
affiliates self-select into the favored arm. Salt the hash, keep the
salt secret, and verify arm assignment server-side for sensitive tests.

## SRM as intrusion signal

Unexpected split skew can indicate bot traffic, scraping, or a broken
deploy hitting one arm - treat SRM flags as potential security events,
not just stats hygiene, and route them to on-call.

## Metric gaming and fraud

Treatment arms that reward behavior (discounts, credits) invite gaming;
guardrails must include abuse/fraud rates, and analysis should segment
suspicious cohorts rather than average them in silently.

## Privacy in segmentation

Fine slices (single store, rare device) re-identify users. Set minimum
cell sizes for segment readouts and suppress small-n slices even when
their p-values look exciting.

## Code-level hygiene (JDK)

Validate x <= n and n > 0 with named-arm exceptions; cast counts to
double before rate math; freeze analysis windows so late events cannot
silently rewrite a shipped decision.

## Peeking as governance failure

Unlogged interim looks with quiet early stops are indistinguishable from
fraud in a regulated readout. Immutable horizon declarations plus access
logs on results dashboards make the procedure auditable.

## Segment fishing for sensitive slices

Trawling subgroups can surface "effects" on protected classes that read
as targeting. Pre-commit segments, apply multiplicity accounting, and
review slice claims for both statistics and disparate impact.

## Results-dashboard access

Pre-readout metric access lets teams trade on or sabotage running tests.
Gate interim dashboards to health metrics only, log goal-metric views,
and freeze the viewer list with the horizon declaration.
