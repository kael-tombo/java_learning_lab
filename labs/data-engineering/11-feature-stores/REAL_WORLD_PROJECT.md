# Feature Stores — REAL WORLD PROJECT

## Context

A fintech runs 180 models in production across fraud, credit, collections, and
marketing. Feature definitions live in 40 SQL files, 12 notebooks, and one
engineer's memory. Serving features are computed by a separate service that
re-implements 60 of them. Twice in the last year a model silently degraded
because a feature's serving implementation drifted from its training
definition. You own the feature platform.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Features | 640 registered, 410 online, 60 with duplicate implementations |
| Online read | 1.1M lookups/sec peak, p99 budget 3ms |
| Entities | 90M customers, 2.4M merchants |
| Offline compute | daily full + hourly incremental, 2.5h window |
| Freshness SLO | online features <= 15 min stale for behavioral signals |
| Storage | 1.8PB feature history, 7y retention |
| Regulatory | model risk management requires feature lineage and reproducibility |
| Constraint | cannot break 180 live models during migration |

## Architecture (target)

```
                +-- feature definitions (versioned SQL / transforms) --+
                |                                                      |
        feature registry (metadata, owner, ttl, lineage, version)     |
                |                                                      |
   +------------+-------------------------------+                     |
   |            |            |                |                     |
offline     offline      offline           online                   |
(batch)     (streaming)  (point-in-time)    (materialized)            |
   |            |            |                |                     |
 parquet    kv store     training sets     Redis/RocksDB cluster     |
                                              |                     |
                                       serving path (<3ms p99)      |
                                              |                     |
                                     feature freshness / parity SLIs
```

## Key Implementation — the three problems, and the fixes that worked

**Problem 1: Training/serving skew.** The serving service implemented features
in Java, the training SQL in SQL, and they were subtly different: one used
`NOW()`, the other the event timestamp; one rounded, the other did not.

```java
/**
 * Parity is enforced in CI, not in a document.
 * The same feature definition produces the offline value and the online value;
 * a transformation library is shared, so there is exactly one implementation.
 */
public interface FeatureTransform {
    String name();
    Object apply(FeatureRow row, Instant asOf);      // asOf is explicit, never NOW()
}

/** Registered once, materialized to both tiers. */
public final class SharedTransforms {
    public static final FeatureTransform ORDERS_30D = row -> {
        Instant asOf = row.asOf();                   // passed in, not read from the clock
        long count = row.stream("orders")
                      .filter(o -> o.ts().isAfter(asOf.minus(Duration.ofDays(30)))
                               && !o.ts().isAfter(asOf))
                      .count();
        return count;                                 // a long: exact, and identical in both tiers
    };

    public static final FeatureTransform AVG_SESSION_SEC = row -> {
        double total = 0; int n = 0;
        for (Session s : row.sessions()) {
            if (s.end().isAfter(row.asOf().minus(Duration.ofDays(7)))) {
                total += s.durationSeconds(); n++;
            }
        }
        return n == 0 ? 0.0 : round6(total / n);     // explicit rounding, same in both tiers
    };
}
```

FLOAT features were the worst offenders, so the convention became: online
features are integers, decimals, or strings. No doubles. Rounding divergence
stopped being a class of bug.

**Problem 2: point-in-time correctness at scale.** The naive correlated join
was 40x slower than the LATERAL version on 90M entities, and a
"latest value wins" implementation leaked the future in three of eleven models
(a real, measurable offline AUC inflation of +0.06).

```java
/**
 * The invariant: for a label at label_ts, only feature rows with
 * event_ts <= label_ts are visible. Enforced in one place so no feature
 * can bypass it, and asserted by a leak test in the feature's CI job.
 */
public final class PointInTimeJoin {
    public static <F> List<F> join(List<Label> labels, List<F> features,
                                    BiPredicate<F, Instant> visibleAt) {
        Map<EntityKey, List<F>> index = features.stream()
                .collect(Collectors.groupingBy(F::entityKey,
                        TreeMap.comparing(F::eventTs).reversed()));   // newest first
        List<F> out = new ArrayList<>(labels.size());
        for (Label label : labels) {
            for (F f : index.getOrDefault(label.entityKey(), List.of())) {
                if (!f.eventTs().isAfter(label.labelTs()) && visibleAt.test(f, label.labelTs())) {
                    out.add(f);
                    break;                                            // newest visible
                }
            }
        }
        return out;
    }
}
```

**Problem 3: freshness and staleness as a first-class signal.** Behavioral
features (sessions, velocity) go stale in minutes; static ones (country, KYC
tier) do not. Per-feature TTLs, and a per-feature SLO, made the difference
explicit.

```java
public enum FreshnessClass {
    STATIC(Duration.ofDays(7)),        // KYC tier, country, device class
    SLOW(Duration.ofHours(6)),         // lifetime value, churn propensity
    BEHAVIORAL(Duration.ofMinutes(15)) // session gap, velocity
}

public record FreshnessSlo(String feature, Duration target, Duration actual) {
    public boolean breached() { return actual.compareTo(target) > 0; }
    /** Behavioral features falling back to a stale value is worse than absent:
     *  a model trained with fresh values gets different inputs at serving time. */
    public boolean shouldServeStale() { return this.breached() && feature.startsWith("stat_"); }
}
```

## Migration Plan (16 weeks, no model downtime)

1. **Weeks 1-3 — Inventory.** All 640 features catalogued with owner, consumers,
   TTL, and which of the 60 duplicates are wrong. Result: 60 duplicate
   implementations retired before any other work.
2. **Weeks 4-7 — Definitions.** Move the 200 highest-traffic features to the
   shared transform library, with a parity test each. Result: parity mismatches
   drop from 60 to 0 on the migrated set.
3. **Weeks 8-11 — Offline materialization.** Point-in-time training sets for all
   models; three models' offline AUC changed once, and each change was traced to
   a leakage fix rather than a regression.
4. **Weeks 12-16 — Online cutover, per model.** Shadow-read the online store
   alongside the existing service for 48h, compare values, then switch traffic
   one model at a time.

## Failure Modes and the Runbook

1. **Parity mismatch after a change.** Symptom: model inputs differ between
   training and serving. Fix: parity test in CI blocks the merge; a mismatch is
   a release blocker, not a follow-up ticket.
2. **Online store eviction storm.** Symptom: p99 spikes to 40ms, cache hit rate
   drops. Cause: a key explosion (an entity id that is actually a composite).
   Fix: key cardinality monitoring and a per-tenant quota.
3. **Stale behavioral features.** Symptom: model accuracy drifts downward within
   hours of a traffic change. Fix: freshness SLO, and a "feature too stale" flag
   passed to the model so it can fall back rather than trust bad inputs.
4. **Point-in-time join regression.** Symptom: offline AUC drops unexpectedly
   after a refactor. Fix: the leak test in CI compares the join against a
   reference implementation on a small fixture.
5. **Backfill cost explosion.** Symptom: a definition change triggers 7 years of
   recompute. Fix: version features rather than editing them; backfill only the
   window the affected models actually train on.
6. **Feature ownership vacuum.** Symptom: nobody can answer "why is this
   40" in the model. Fix: registry requires an owner; an unowned feature cannot
   be promoted, and the registry is the source for model-risk documentation.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Feature stores are a pattern for defining, storing, and serving ML features,
  with an offline store for training and an online store for low-latency
  serving; the training/serving skew problem is the core motivation.
  - Reference: https://feast.dev/
  - Reference: https://docs.feast.dev/
- Point-in-time-correct joins (as-of joins) are required for unbiased training
  data because a naive join leaks future information into the feature set.
  - Reference: https://docs.feast.dev/getting-started/concepts/point-in-time-joins
  - Reference: https://en.wikipedia.org/wiki/Lookahead_bias

## Deliverables
- [ ] Feature inventory with owners, consumers, TTLs, and duplicate resolution
- [ ] Shared transform library with the integer-online-feature convention
- [ ] Point-in-time join with a leak test and an offline AUC impact statement
- [ ] Per-feature-class freshness SLOs with a stale-serve policy
- [ ] CI parity tests per feature, enforced as merge blockers
- [ ] 16-week migration plan with shadow-read cutover
- [ ] Runbook for the six failure modes
