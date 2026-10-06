# Feature Store Architecture - Code Deep Dive

**Track:** mlops  |  **Lab:** lab04  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. Module Map

```text
src/
  FeatureStoreLab.java          driver: defines views, materialises, tests parity
  FeatureView.java              versioned definition: entity, features, semantics, owner
  OfflineStore.java             Parquet-style history preserving event timestamps
  OnlineStore.java              Redis-like latest-value store with per-feature TTL
  Materializer.java             one transformation -> both stores, with lag metrics
  PointInTimeJoin.java          lookback-window join for training rows
  FreshnessMonitor.java         per-feature freshness and staleness rate with alerts
```

Materializer has exactly one transformation method. If you find yourself adding a second path for the online store, that is the moment skew starts.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `FeatureView` | name, version, entity key, feature semantics, owner, TTL |
| `Materializer` | one transform feeding offline and online; records lag per stage |
| `PointInTimeJoin` | lookback-window join returning only values available at label time |
| `FreshnessMonitor` | per-feature freshness, staleness rate, alert threshold |

---

## 3.1 One transformation, two stores

The transform is written once and called for both projections. The lag timings are recorded per stage so the SLO can be attributed.

```java
public MaterializationResult materialize(FeatureView view, Instant windowEnd) {
    long tIngest = now(), tCompute, tWrite;
    List<Row> rows = source.scan(view.source(), windowEnd);   // preserves event_ts
    tCompute = now();
    for (Row r : rows) {                                     // ONE definition
        Map<String, Value> f = view.transform().apply(r);
        offline.upsert(view.name(), r.entity(), f);          // history, event_ts kept
        for (var e : f.entrySet())
            online.put(view.name(), r.entity(), e.getKey(), e.getValue(), view.ttl(e.getKey()));
    }
    tWrite = now();
    return new MaterializationResult(rows.size(),
            lag(tIngest, tCompute), lag(tCompute, tWrite), lag(tIngest, tWrite));
}
```


---

## 3.2 Point-in-time join that cannot see the future

For each label, walk the entity's feature events backwards until one is at or before the cutoff. A naive 'latest value' join is what leaks.

```java
public Map<String, Value> featuresAt(String entity, Instant labelTime,
                                       Duration lookback, OfflineStore store) {
    Instant cutoff = labelTime.minus(lookback);      // strict: never after this
    List<Event> events = store.eventsFor(entity);
    Map<String, Value> out = new HashMap<>();
    for (Event e : events) {                          // events sorted ascending
        if (e.ts().isAfter(cutoff)) continue;         // drop anything from the future
        out.put(e.feature(), Value.of(e.value(), e.ts()));   // latest wins, <= cutoff
    }
    return out;
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Batch materialisation | `O(rows x features)` | dominated by source scan and write amplification |
| Online feature read, batched | `O(1) round trips` | latency dominated by network, not payload |
| Point-in-time join per row | `O(log n) with an indexed lookup` | avoid a full scan per row |
| Parity check | `O(entities sampled)` | sample daily, assert on 100% of critical features |

## 5. Correctness and Numerics

- Preserve event timestamps end to end; without them point-in-time joins are impossible.
- Batch online reads into one call per entity.
- Use per-feature TTLs; a global TTL is a compromise nobody chose.
- Round consistently in the transform, never in the consumer.
- Assert parity in CI between offline and online for a sample of entities.

## 6. Test Strategy

- Offline and online return identical values for the same entity after materialisation.
- A point-in-time join never returns a feature value later than the cutoff.
- A feature with a stale upstream source triggers a staleness alert at the configured threshold.
- A new feature version does not change results for the previous version.
- An expired TTL removes the online value and the read fails loudly.
- Owner and semantics are required to register a feature view.

## 7. Extension Points

- Add push materialisation for a real-time counter alongside pull for aggregates.
- Implement a feature registry with deprecation and usage tracking.
- Compute reuse ratio and surface it as the platform's adoption metric.

## 8. Review Checklist

- [ ] One transform, both stores, no second implementation
- [ ] Event timestamps preserved through to the offline store
- [ ] Point-in-time joins use an explicit lookback
- [ ] Per-feature TTLs and freshness metrics
- [ ] Parity between stores tested in CI
- [ ] Feature views versioned, owned and deprecatable
