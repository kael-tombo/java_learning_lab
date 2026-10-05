# Feature Stores — MINI PROJECT

## Project: Minimal Feature Store with Offline and Online Parity

A two-tier feature store: a registry of feature definitions, an offline
(point-in-time correct) materializer, an online store (in-memory/Redis-like),
and a parity checker.

### Scope
- Registry: `FeatureSpec(name, entity, sql expression, ttl, owner, version)`.
- Offline: materialize a training set with an as-of join, keyed by `event_ts`.
- Online: upsert computed features with TTL, point lookup by entity.
- Parity: compare offline vs online for the same `(entity, event_ts)`.
- Registry tests: TTL required, owner required, no duplicate names.

### Architecture

```
raw events (orders, sessions)         entity table (users)
        |                                    |
        +------------+-----------------------+
                     |
        [OfflineFeatureStore]
        materialize as-of  (event_ts <= label_ts, ORDER BY + RANGE join)
                     |
              training set (offline)
                     |
             +-------+-------+
             |               |
        [OnlineStore]   [Model training]
        upsert+TTL      read training set
             |
        [Serving path]  point lookup by entity, <5ms p99
             |
        [ParityChecker]  offline vs online, per feature, per day
```

### Implementation

```java
public record FeatureSpec(String name, String entityKey, String sqlExpr,
                          Duration ttl, String owner, int version, boolean online) {
    public String qualifiedName() { return entityKey + "." + name; }
}

public final class FeatureRegistry {
    private final Map<String, FeatureSpec> specs = new LinkedHashMap<>();

    public void register(FeatureSpec spec) {
        Objects.requireNonNull(spec.ttl(), "every online feature needs a TTL: " + spec.name());
        Objects.requireNonNull(spec.owner(), "every feature needs an owner: " + spec.name());
        if (!spec.name().matches("[a-z0-9_]+")) {
            throw new IllegalArgumentException("feature names must be snake_case: " + spec.name());
        }
        if (specs.putIfAbsent(spec.qualifiedName(), spec) != null) {
            throw new IllegalStateException("duplicate feature " + spec.qualifiedName()
                    + "; bump the version instead of overwriting");
        }
    }
}
```

### Point-in-time-correct offline materialization

This is the core correctness problem. Joining features to labels without an
as-of constraint leaks the future into training.

```java
public final class OfflineFeatureStore {
    /**
     * For each label row (entity, label_ts), pick the most recent feature row
     * with event_ts <= label_ts. Not "the latest row overall" - that is leakage.
     */
    public List<FeatureRow> buildTrainingSet(List<LabelRow> labels,
                                             Map<String, List<FeatureRow>> features) {
        List<FeatureRow> out = new ArrayList<>(labels.size());
        for (LabelRow label : labels) {
            Map<String, Object> values = new HashMap<>();
            features.forEach((fname, rows) -> {
                FeatureRow pick = rows.stream()
                        .filter(r -> r.entity().equals(label.entity()))
                        .filter(r -> !r.eventTs().isAfter(label.labelTs()))
                        .max(Comparator.comparing(FeatureRow::eventTs))
                        .orElse(null);
                if (pick != null) values.put(fname, pick.values());
            });
            out.add(new FeatureRow(label.entity(), label.labelTs(), values, label.label()));
        }
        return out;
    }
}
```

The equivalent SQL, which is what most systems actually run:

```sql
-- point-in-time correct: the correlated subquery bounds by event_ts
SELECT l.entity_id, l.label, l.label_ts,
       f1.orders_30d, f2.last_session_gap_hours, f3.lifetime_value
  FROM labels l
  LEFT JOIN LATERAL (
        SELECT orders_30d FROM feat_user_agg
         WHERE entity_id = l.entity_id AND event_ts <= l.label_ts
         ORDER BY event_ts DESC LIMIT 1) f1 ON TRUE
  LEFT JOIN LATERAL (
        SELECT last_session_gap_hours FROM feat_session_stats
         WHERE entity_id = l.entity_id AND event_ts <= l.label_ts
         ORDER BY event_ts DESC LIMIT 1) f2 ON TRUE
  LEFT JOIN LATERAL (
        SELECT lifetime_value FROM feat_user_value
         WHERE entity_id = l.entity_id AND event_ts <= l.label_ts
         ORDER BY event_ts DESC LIMIT 1) f3 ON TRUE;
```

### Online store

```java
public final class OnlineStore {
    private final Map<String, Map<String, Expiring>> data = new ConcurrentHashMap<>();

    record Expiring(Map<String, Object> values, Instant writtenAt, Duration ttl) {
        boolean expired(Instant now) { return now.isAfter(writtenAt.plus(ttl)); }
    }

    public void upsert(String entity, Map<String, Object> values, Map<Duration> ttls, Instant now) {
        Map<String, Expiring> row = data.computeIfAbsent(entity, k -> new ConcurrentHashMap<>());
        values.forEach((k, v) -> {
            Duration ttl = ttls.getOrDefault(k, Duration.ofDays(30));
            row.put(k, new Expiring(Map.of(k, v), now, ttl));
        });
        sweeper.scheduleAtFixedRate(() -> evict(now()), 1, 1, TimeUnit.HOURS);
    }

    public Map<String, Object> get(String entity, List<String> names, Instant now) {
        Map<String, Expiring> row = data.getOrDefault(entity, Map.of());
        Map<String, Object> out = new HashMap<>();
        for (String n : names) {
            Expiring e = row.get(n);
            if (e != null && !e.expired(now)) out.put(n, e.values().get(n));
        }
        return out;
    }

    private void evict(Instant now) {
        data.values().forEach(row -> row.entrySet().removeIf(e -> e.getValue().expired(now)));
    }
}
```

### Parity checker

```java
public record ParityResult(String feature, long compared, long mismatches,
                           double maxAbsDiff, List<String> examples) {
    boolean ok() { return mismatches == 0; }
}

public final class ParityChecker {
    /**
     * Compare the value the model saw offline with the value it gets online.
     * Any systematic difference is a correctness bug, not a rounding curiosity:
     * it means training and serving are computing different things.
     */
    public ParityResult compare(String feature, List<FeatureRow> offline,
                                BiFunction<String, List<String>, Map<String, Object>> onlineFetch) {
        long compared = 0, mismatches = 0;
        double maxDiff = 0;
        List<String> examples = new ArrayList<>();
        for (FeatureRow row : offline) {
            Object off = row.values().get(feature);
            Object on = onlineFetch.apply(row.entity(), List.of(feature)).get(feature);
            if (off == null && on == null) continue;
            compared++;
            double diff = numericDiff(off, on);
            maxDiff = Math.max(maxDiff, diff);
            if (diff > 1e-6) {
                mismatches++;
                if (examples.size() < 5) {
                    examples.add(row.entity() + "@" + row.eventTs()
                            + " offline=" + off + " online=" + on);
                }
            }
        }
        return new ParityResult(feature, compared, mismatches, maxDiff, examples);
    }
}
```

### Test It

```java
@Test void noFutureLeakage() {
    List<LabelRow> labels = List.of(new LabelRow("u1", Instant.parse("2026-01-10T00:00:00Z"), 0));
    // A feature row dated AFTER the label: must be excluded.
    List<FeatureRow> features = List.of(
            new FeatureRow("u1", Instant.parse("2026-01-09T00:00:00Z"), Map.of("orders_30d", 3), null),
            new FeatureRow("u1", Instant.parse("2026-01-20T00:00:00Z"), Map.of("orders_30d", 99), null));

    var row = store.buildTrainingSet(labels, Map.of("orders_30d", features)).get(0);
    assertEquals(3, row.values().get("orders_30d"));     // NOT 99
}

@Test void onlineAndOfflineAgree() {
    // ... materialize, upsert online, then compare
    assertTrue(checker.compare("orders_30d", offlineRows, store::get).ok());
}
```

### Stretch
- Add a feature-drift monitor comparing serving distributions to the training baseline.
- Implement a versioned deprecation: mark `v1` deprecated, keep materializing for 90 days, alert consumers.
- Add a materialization job that only recomputes changed partitions.

## Deliverables
- [ ] Feature registry with TTL/owner enforcement and versioning
- [ ] Point-in-time-correct offline materializer, with a leak test
- [ ] Online store with TTLs, partial updates, and eviction
- [ ] Parity checker with a per-feature report
- [ ] Feature drift monitor against a training baseline
- [ ] Deprecation flow that breaks no consumer
