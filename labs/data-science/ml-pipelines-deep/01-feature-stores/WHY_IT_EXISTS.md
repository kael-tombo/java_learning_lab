# Feature Stores — Why It Exists

Models kept failing for unglamorous reasons: a notebook computed
features one way, the service another; a join peeked at the future;
nobody could rebuild last month's training set. Each incident looked
like a modeling problem but was a plumbing problem.

The feature store exists to make feature plumbing explicit and
auditable: one versioned definition, one history log, one serving path.
It trades a small upfront cost (register, version, backfill) for the
ability to answer "what exactly did this model see?" months later.
Without it, every model carries hidden dependencies on forgotten SQL.

Concretely, three recurring incidents motivate the three contracts.
Future leakage (fixed by as-of joins) once inflated a team's offline
metrics until launch day exposed the gap — the demo's 1.0 row bias is
that incident in miniature. Transform drift (fixed by shared versioned
code) once degraded a model gradually as the service's copy of a
transform aged — the demo's 1.0 maxdiff is that drift's signature.
Stale reads after an upstream outage (fixed by TTLs) once served
week-old values as if fresh — the demo's 0.5 coverage shows the
mechanism that would have caught it.

The store does not improve models; it makes model quality measurable
by removing the plumbing confounders. That is why it precedes modeling
work in this track: no evaluation (lab 03) is valid on leaked rows, and
no pipeline (lab 02) is reproducible on unversioned features.
