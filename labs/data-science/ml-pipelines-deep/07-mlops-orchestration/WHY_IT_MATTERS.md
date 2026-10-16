# MLOps Orchestration - Why It Matters

Cadence decides model freshness: scheduled plus event-driven runs keep models current without heroics.

Gates decide blast radius: metric-gated promotion keeps regressions out of production instead of paging about them later.

Lineage decides auditability: data, code, parameters, and environment per run answer what changed and what to revert.

Idempotent retries decide reliability: transient outages become delays rather than duplicated side effects and corrupt state.

Backfill capability decides recovery speed. History repair as routine replay beats emergency surgery on live tables.

Queue separation decides fairness between live work and replays. Shared queues let yesterday's fix starve today's training.

Environment pins decide debuggability. When reruns reproduce exactly, incidents become investigations instead of mysteries.

Trigger choice decides staleness bounds. Cron bounds by clock, events bound by change; together they cover both failure modes.

## Freshness and safety

Retraining cadence decides whether models track the world or memorialize it: cron
bounds staleness by the clock while event triggers bound it by change, and most
systems need both because time passing and the world changing are different risks.
Staleness unmeasured becomes staleness unmanaged.

Gate strictness decides what production never sees: a vetoed candidate costs a
notification while a shipped regression costs an incident. Per-slice bars look
expensive until the first broken segment they stop; then they look like the
cheapest insurance in the building.

## Reliability mechanics

Idempotent retries convert outages into delays: the same transient failure that
duplicates side effects in sloppy DAGs merely overwrites identical outputs in
careful ones. Reliability here is a write-keying discipline, not heroism.

Queue separation converts replays from threats into routine: backfills proceed at
capped concurrency in their own lane while scheduled runs keep their cadence.
Shared queues make every history repair a live-training outage wearing a disguise.

## Audit and learning

Lineage completeness decides whether incidents are solvable: with data, code,
parameters, and environment recorded, each divergence names its unpinned input.
Without them, reruns disagree and nobody can say why, which is the precise shape
of an unlearnable lesson.

Promotion records decide accountability: who shipped which lineage pointer when,
against which gate snapshot. Reverts follow the pointer home instead of hunting
through chat logs, and the next incident starts from evidence rather than rumor.

Trigger ownership decides hygiene: each cadence with one firing mechanism and a
reviewed inventory means no zombie schedule double-trains in the background. The
quarterly inventory is cheap; the duplicate runs it deletes are not.
