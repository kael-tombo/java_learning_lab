# Feature Stores — Theoretical Foundation

## Core Concept

A feature store is a managed layer between raw data and model training /
serving with one job: **every feature value a model trains on must be
reproducible at serve time, and every served value must be fresh enough to
matter**. It splits into two stores with opposite optimizations:

| | Offline store | Online store |
|---|---|---|
| Reads | bulk scans (training sets) | point lookups by key (µs–ms) |
| Writes | batch backfills, immutable history | streaming/low-latency upserts |
| Consistency demand | complete history, replayable | freshest value per key |
| Typical backing shape | columnar files / warehouse tables | key-value / document lookup |

Same logical features, two physical systems, one contract gluing them:
**point-in-time correctness**.

## Point-in-Time Correctness (the load-bearing rule)

Training rows join events to features **as of the event timestamp** —
the latest feature value *at or before* the event, never after:

```
event @ t=10  →  feature snapshot @ t=8   (correct)
event @ t=10  →  feature snapshot @ t=12  (LEAKAGE: future information)
```

Joining the *current* feature value instead of the *as-of* value leaks the
future into training: the model learns from information it will never have
at serve time, inflating offline metrics that collapse in production. The
as-of join (temporal join, `FOR SYSTEM_TIME AS OF` in streaming SQL
dialects) is the mechanism; "no future leakage" is the invariant every
audit checks first.

## Training/Serving Skew and Its Sources

Even with correct joins, training and serving diverge through:

1. **Pipeline skew** — batch features (recomputed nightly) vs served
   features (computed inline): different code paths, different bugs.
   Fix: shared transformation definitions (one function, two runners).
2. **Staleness skew** — online value lags the event (streaming delay,
   TTL expiry): the model sees older features than training assumed.
   Fix: freshness SLOs + staleness monitoring, not hope.
3. **Feedback skew** — served predictions influence future training labels
   (recommendation loops, fraud-model retraining on caught fraud only).
   Fix: logging the *served* feature values alongside predictions so
   retraining replays reality, not the offline ideal.

## Versioning, Backfill, Retention

- **Versioning**: feature definitions (not just values) are versioned —
  retraining six months later must resolve the *same transformation code*,
  or the replay is fiction. Pin code + data snapshots together.
- **Backfill**: recomputing history after a definition change or outage.
  Backfills must respect as-of semantics *and* quarantine: never mix
  backfilled ranges with live ranges without marking provenance, or
  downstream consumers can't distinguish recomputation artifacts.
- **Retention/TTL**: online stores expire keys (cost + relevance); offline
  stores retain per compliance *and* per retraining horizon. Deleting
  online state a model still expects is a silent accuracy incident —
  retention policy is a model contract, not janitorial detail.

## Key Invariants

1. Training joins are as-of-event-time, never as-of-now.
2. Every served feature has a freshness SLO; staleness is monitored, not
   assumed away.
3. Feature definitions are versioned with their values; replay resolves
   both.
4. Logged serving-time values (not offline ideals) feed retraining.
5. Online/offline are two views of one logical feature set — drift between
   the views is a bug, not a property.
