# Real-Time Feature Store — REAL WORLD PROJECT

## Context

A payments company serves a real-time fraud model on 40k authorizations per
second at peak. Feature values come from a Redis cluster, a JVM local cache,
and a batch job that writes them hourly. During a network partition, a third of
feature lookups returned null; the model's behaviour changed because of it, and
the fraud team found out from false negatives rather than from an alert. You own
the feature serving layer and its degradation behaviour.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Entities | 90M cards, 2.4M merchants, 14M devices |
| Read QPS | 40k peak, 6k average; 320 features requested per decision |
| Latency budget | p99 < 3ms for the whole feature fetch, 120ms for the full decision |
| Stores | Redis Cluster (24 shards), JVM L1 caches, hourly batch materialization |
| Freshness | behavioural features <= 5 min; static features <= 24h |
| Availability | feature store must not be a new single point of failure |
| Constraint | cannot change the model; the serving contract must stay compatible |
| Evidence | decisions are audited; features used must be reconstructable |

## Architecture (target)

```
sources
  |-- Kafka (auth events)          --> stream job --> partial feature updates
  |-- batch warehouse (hourly)     --> bulk feature load
  |-- static reference (daily)     --> versioned reference features
                    |
        +-----------+-----------+
        |                       |
   ONLINE STORE (Redis)    L1 (JVM, per pod)
   24 shards, RF 2         60s TTL, bounded
        |                       |
        +-----------+-----------+
                    |
           FEATURE SERVING API
           - fan-out read, batched (MGET)
           - per-feature freshness
           - fallback chain, explicit
           - decision audit log
                    |
              fraud model (unchanged)
```

## Key Implementation — the four problems, and what fixed them

**Problem 1: 320 features per decision blew the latency budget.** One Redis
round trip per feature is 320 round trips. The fix is a single pipelined
`MGET` per decision, with features packed into a compact serialized value
rather than 320 hash fields.

```java
public final class BatchedFeatureFetcher {
    /**
     * One MGET, not N GETs. Over a 0.4ms round trip, 320 sequential gets is
     * 128ms; a single pipelined MGET of 320 keys is ~1.1ms.
     */
    public Map<String, Object> fetch(String entityKey, List<String> features) {
        List<String> keys = features.stream().map(f -> entityKey + ":" + f).toList();
        List<byte[]> raw = redis.mget(keys.toArray(new String[0]));   // one round trip

        Map<String, Object> out = new HashMap<>(features.size());
        for (int i = 0; i < features.size(); i++) {
            byte[] v = raw.get(i);
            if (v == null) continue;
            FeatureEnvelope env = CODEC.decode(v);
            out.put(features.get(i), env.value());
            out.put("__meta:" + features.get(i), new FeatureMeta(env.writtenAt(), env.ttl()));
        }
        return out;
    }
}
```

**Problem 2: staleness was invisible, so the model trusted bad inputs.** The
response now carries per-feature freshness, and the decision audit log records
it. This is what turns "the model behaved differently" into an answerable
question.

```java
public enum ServingPolicy { SERVE_FRESH, SERVE_WITH_FLAG, REFUSE }

public final class FreshnessPolicy {
    /**
     * Three policies, decided per feature, because a stale value is not always
     * equally harmful:
     *
     *   SERVE_FRESH  - never serve beyond TTL. Correct for anything where a
     *                  wrong value causes a wrong decision (velocity, limits).
     *   SERVE_WITH_FLAG - serve beyond TTL but mark it, so the model can reduce
     *                  confidence or route to manual review (device, geo).
     *   REFUSE       - if missing or stale, the decision is not made. Used for
     *                  features under regulatory control (sanctions list).
     *
     * Note the cost of the choice: REFUSE features make the whole decision
     * unavailable, so they get a local mirror with its own SLO.
     */
    private static final Map<String, ServingPolicy> POLICIES = Map.ofEntries(
            Map.entry("velocity_1m", ServingPolicy.SERVE_FRESH),
            Map.entry("velocity_24h", ServingPolicy.SERVE_FRESH),
            Map.entry("device_trusted", ServingPolicy.SERVE_WITH_FLAG),
            Map.entry("last_geo", ServingPolicy.SERVE_WITH_FLAG),
            Map.entry("on_sanctions_list", ServingPolicy.REFUSE));

    public Decision support(FeatureResponse r, String feature) {
        ServingPolicy p = POLICIES.getOrDefault(feature, ServingPolicy.SERVE_WITH_FLAG);
        Freshness f = r.freshnessOf(feature);
        return switch (p) {
            case SERVE_FRESH       -> f == Freshness.FRESH ? Decision.accept(r)
                                                        : Decision.defer("stale: " + feature);
            case SERVE_WITH_FLAG   -> f == Freshness.MISSING ? Decision.acceptMissing(r)
                                                        : Decision.accept(r, f);
            case REFUSE            -> f == Freshness.FRESH ? Decision.accept(r)
                                  : Decision.defer("refusing without " + feature);
        };
    }
}
```

**Problem 3: a Redis partition degraded the whole decision path.** The fix is
a fallback chain whose behaviour is defined in advance, and a local mirror for
the `REFUSE` features that cannot tolerate absence.

```java
public final class FeatureResolutionChain {
    public Resolved resolve(String entity, List<String> features, Instant now) {
        Resolved r = new Resolved(entity);
        // L2: online store
        try {
            r.merge(online.fetch(entity, features), Origin.ONLINE);
        } catch (RedisConnectionException e) {
            degraded.mark("online_store_unreachable");
        }
        // L1: JVM local cache (60s TTL), covers a short partition
        r.mergeMissing(localCache.getAll(entity, features), Origin.L1);
        // L0: last-known-good, written by a background job from the audit log
        r.mergeMissing(lastKnownGood.get(entity, features), Origin.LKG);
        // Model default, only for features the model is trained to accept
        r.mergeMissing(defaultsFor(features), Origin.DEFAULT);

        // Whatever we ended up with, record it. A fallback that is invisible
        // is how the original incident happened.
        r.all().forEach((f, v) -> audit.record(entity, f, v, r.originOf(f), now));
        return r;
    }
}
```

The last-known-good store is the quiet part that matters. It is fed by the
decision audit log, so it is always the value that was actually used, not a
recomputed guess — which means a 30-minute partition degrades to "features as
they were 30 minutes ago", which the model has seen before, rather than to
nulls, which it has not.

**Problem 4: no capacity model meant no basis for scaling decisions.** The
footprint is arithmetic, and it is checked against reality quarterly.

```java
/**
 * 90M cards x 320 features, but not all features are on all entities:
 *   behavioural  24 features/entity  -> 2.16B values
 *   derived      48 features/entity  -> 4.32B values
 *   static      248 features/entity  -> 22.3B values (mostly shared per-card defaults)
 *
 * 26 bytes/value (2-8B value + 4B writtenAt + 2B ttl + ~12B key overhead in the
 * MGET key string) x 28.8B values = 750GB raw, x2 RF = 1.5TB, /0.7 utilization
 * = 2.14TB -> 90 nodes of 32GB. Measured steady state: 61% of that, because
 * static features are versioned and shared rather than per-entity.
 */
public record Footprint(long entities, Map<String, Integer> featuresPerClass,
                        int bytesPerValue) {
    public long rawBytes() { return entities * featuresPerClass.values().stream()
            .mapToLong(Integer::longValue).sum() * bytesPerValue; }
    public long clusterBytes(double rf, double util) {
        return (long) Math.ceil(rawBytes() * rf / util);
    }
}
```

## The three changes, measured

| Change | p99 latency | Decision availability | False-negative rate (weekly) |
|---|---|---|---|
| Before | 18.4ms | 99.2% (partitions) | 1.9% |
| Batched MGET | 2.9ms | 99.2% | 1.9% |
| Freshness policy + LKG fallback | 3.1ms | 99.94% | 1.4% |
| Local mirror for REFUSE features | 3.0ms | 99.98% | 1.4% |

Latency went up by 0.2ms for the fallback work. Availability went up 0.78
points. The false-negative rate fell because the model stopped being fed nulls
it was never trained on.

## Failure Modes and the Runbook

1. **Redis partition.** Symptom: connection errors, decision path failing open.
   Fix: L1 cache and LKG absorb it; decisions fall back to 30-minute-old
   features; the audit log makes the degradation queryable after the fact.
2. **Hot key / cardinality explosion.** Symptom: one shard's CPU saturates, p99
   on that shard only. Fix: per-tenant shard budget and hot-key detection; a
   composite key that accidentally collapses to one value is the usual cause.
3. **Streaming job lag.** Symptom: behavioural features go AGING then STALE.
   Fix: per-feature staleness SLOs; the model receives the freshness flag and
   routes to review instead of trusting the value.
4. **Bad feature computation deployed.** Symptom: a feature value is wrong
   across all entities. Fix: shadow compute the new logic, compare distributions
   on 5% of traffic for 24h, then flip; LKG and a versioned feature name allow
   a rollback without downtime because the old name is still populated.
5. **Local cache stampede after a deploy.** Symptom: p99 spike on a cold pod
   because every request goes to the online store. Fix: jittered prefetch on
   warm-up, and a small circuit breaker that serves a bounded LKG snapshot.
6. **Memory exhaustion from an unbounded feature set.** Symptom: evictions, then
   cache misses at scale. Fix: TTL plus an explicit maximum features-per-entity
   enforced at write time; reject the write rather than evict silently.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Online feature stores are built for low-latency serving with the same feature
  definitions used offline, and freshness/staleness handling is a first-class
  concern because online and offline values are updated on different schedules.
  - Reference: https://feast.dev/
  - Reference: https://docs.feast.dev/
  - Reference: (link removed)
- Redis Cluster shards data across hash slots and provides replication; the
  sharding model is why pipelined multi-key reads matter for a many-feature
  serving path.
  - Reference: https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/
  - Reference: https://redis.io/docs/latest/develop/use/pipelining/

## Deliverables
- [ ] Batched multi-key fetch with a single round trip and a latency measurement
- [ ] Per-feature serving policy (serve fresh / serve with flag / refuse)
- [ ] Three-level fallback chain plus an LKG store fed by the decision audit log
- [ ] Local mirror for the refuse-tier features with its own SLO
- [ ] Capacity model with measured vs computed footprint
- [ ] Shadow-compute and feature-version rollback procedure
- [ ] Decision audit log recording value, origin, and freshness per feature
- [ ] Runbook for the six failure modes
