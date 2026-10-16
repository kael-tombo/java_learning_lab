# MLOps Orchestration - Why It Exists

Retraining by hand works once and fails at cadence: skipped validations, unrecorded parameters, mystery production models.

Orchestration exists to make the path from data to promoted model repeatable, gated, and auditable. DAGs order the work; lineage records what happened; gates stop bad candidates.

Retries with backoff exist because dependencies fail transiently; idempotence exists so those retries are safe.

Backfill exists because history needs repair after bugs; versioned replays beat ad-hoc patches applied to live data.

Triggers exist because staleness has two causes: time passing and the world changing. Cron covers the first, events cover the second.

Environment pins exist because unrecorded upgrades silently change results. Reproducibility is a debuggability requirement, not paperwork.

Data-validation gates exist because training on corrupt input wastes the most expensive step. Cheap checks first, GPUs later.

Metric gates exist because averages promote regressions. Per-slice bars keep one broken segment from shipping inside a good-looking overall lift.

## Why each piece exists

Idempotence exists because retries are certain: dependencies fail transiently, and
a rerun that duplicates outputs turns every hiccup into corruption. Keying writes
by run id converts the same hiccup into an identical overwrite, which is safety
by construction rather than by luck.

Capped backoff exists because eagerness synchronizes: uncapped parallel retries
hammer a recovering dependency in lockstep and convert its outage into a second
one. Doubling waits with a cap and jitter turns a stampede into a queue.

Lineage exists because production models need biographies: data version, code
commit, parameters, and environment pin answer what changed and what to revert.
A model without lineage is an orphan; incidents involving orphans become mysteries
instead of investigations.

Metric gates exist because averages promote regressions: overall lift clears while
one slice collapses, and only the conjunction — lift plus every no-regression bar —
stops that shipment. The veto is the mechanism, not bureaucracy.

## What orchestration refuses to do

Orchestration refuses side effects inside retried tasks: traffic moves and charges
happen behind promotion flags, never where backoff can replay them. Exactly-once
effects come from flag-then-act ordering, not from hoping retries stay quiet.

Orchestration refuses live-path backfills: history repair writes versioned outputs
that consumers adopt explicitly, because patching live tables rewrites the past
every reader already built upon. Reprints, not white-out.

Orchestration refuses unpinned reruns: lockfiles, seeds, commits, and data versions
are recorded per run so equality is checkable. A rerun that cannot reproduce its
fingerprint indicts its inputs before it indicts its code.
