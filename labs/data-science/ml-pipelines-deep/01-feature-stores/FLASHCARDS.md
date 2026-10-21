# Feature Stores — Flashcards

Q: Offline store vs online store?
A: Offline holds full (entity, ts, value) history for training joins;
online holds the latest vector per entity for low-latency serving.

Q: Point-in-time correctness in one sentence?
A: A training row at label time t may only use feature rows with
ts <= t, taking the latest such row per feature.

Q: What breaks if the join allows ts > t?
A: Future leakage: the model trains on data unavailable at serving
time; verified bias of 1.0 on the demo row (3.0 vs 2.0).

Q: What is serving skew?
A: Training and serving compute different vectors for the same entity,
usually from divergent transform code or defaults.

Q: How is skew detected numerically?
A: Recompute expected vectors offline and take per-feature max absolute
difference; demo gives 0.0 consistent, 1.0 with a stale shift.

Q: Why version features?
A: So definition changes do not silently alter deployed models;
training rows pin (name, version) and old versions stay readable.

Q: What is a backfill?
A: Recomputing history with a new versioned transform in ts order,
validated before the version goes live.

Q: What does TTL do?
A: Treats values older than TTL as missing at read time; demo
TTL=30 at t=100 keeps 2 of 4 rows (coverage 0.5).

Q: Offline/online must share what?
A: The transform code. Sharing code is the main structural defense
against skew.

Q: What does the materializer do?
A: Streams offline rows into the online store via idempotent upserts
keyed by (entity, ts), ignoring older ts on retry.
