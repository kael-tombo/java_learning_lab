# Apache Flink (Advanced) — REAL WORLD PROJECT

## Context

A large European bank's real-time risk platform runs 40+ Flink jobs on a shared
Kubernetes cluster. Following a platform migration, latency doubled, one job
holds 2.4TB of state, checkpoint failures are routine, and two teams run
near-duplicate CEP jobs. Your mandate: consolidate, re-architect for
statefulness, and restore the latency SLO.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Jobs | 43 (14 duplicated in at least two forms) |
| Throughput | 310k events/sec across 6 topic domains |
| Largest job state | 2.4TB (velocity counters, 400 days) |
| Latency SLO | p99 decision < 60ms for card-not-present fraud |
| Availability | 99.95%; a missed fraud decision is a regulatory event |
| Cluster | Kubernetes, 3 AZ, spot + on-demand mix, autoscaling |
| Constraint | deployments are weekly and cannot require downtime |

## Architecture (target)

```
                         +-- domain 1: card fraud (CEP, p=192, 60ms SLO)
Kafka (6 domains) ------+
                         +-- domain 2: AML transaction monitoring (Table API, p=128)
                         |
                         +-- domain 3: liquidity / exposure (Table API, p=96)
                         |
                         +-- domain 4-6: consolidated feature jobs (p=64 each)

consolidation moves:
  - 14 duplicate CEP jobs  -> 3 shared pattern libraries
  - per-team DataStream   -> 1 Table API convention for aggregations
  - unbounded ListState   -> keyed aggregators with TTL (2.4TB -> 340GB)

sinks: one exactly-once lakehouse sink pattern, reused
```

## Key Implementation — state reduction as the primary fix

2.4TB of state was not a size problem; it was a modelling problem. The job
stored every transaction in a `ListState` and scanned it on every event.

```java
/** Before: 2.4TB ListState, O(n) scan per event, checkpoint 40s+, failing often. */
public class NaiveVelocity extends KeyedProcessFunction<String, Txn, Alert> {
    private transient ListState<Txn> history;
    public void processElement(Txn t, Context ctx, Collector<Alert> out) throws Exception {
        List<Txn> all = IteratorUtils.toList(history.get());
        all.add(t);
        // ... scan all to find transactions in the last 60 minutes
    }
}

/** After: O(1) updates, TTL-bounded, ~340GB total, checkpoint 6s. */
public class BucketedVelocity extends KeyedProcessFunction<String, Txn, Alert> {
    private transient MapState<Long, Bucket> buckets;   // epochMinute -> count+sum
    private static final int WINDOW_MINUTES = 60;

    public void processElement(Txn t, Context ctx, Collector<Alert> out) throws Exception {
        long minute = t.ts().getEpochSecond() / 60;
        Bucket b = buckets.get(minute);
        if (b == null) b = new Bucket();
        b.add(t.amount());
        buckets.put(minute, b);

        // Register a cleanup timer at the window edge instead of holding history.
        ctx.timerService().registerEventTimeTimer((minute + WINDOW_MINUTES) * 60_000L);

        long windowCount = 0; BigDecimal windowSum = BigDecimal.ZERO;
        for (Map.Entry<Long, Bucket> e : buckets.entries()) {
            if (e.getKey() >= minute - WINDOW_MINUTES) {
                windowCount += e.getValue().count(); windowSum = windowSum.add(e.getValue().sum());
            }
        }
        if (windowCount >= velocityLimit || windowSum.compareTo(amountLimit) > 0) {
            out.collect(new Alert(t.account(), windowCount, windowSum, t.ts()));
        }
    }

    @Override public void onTimer(long ts, OnTimerContext ctx, Collector<Alert> out) throws Exception {
        long expired = ts / 60_000L - WINDOW_MINUTES;
        for (Long k : new ArrayList<>(buckets.keys())) {
            if (k < expired) buckets.remove(k);            // bounded, provably
        }
    }
}
```

The numbers that followed are the argument for the refactor:

| Metric | Before | After |
|---|---|---|
| State | 2.4TB | 340GB |
| p99 latency | 310ms | 47ms |
| Checkpoint duration | 40-90s (frequent failures) | 6.2s |
| Checkpoint success rate | 78% | 99.6% |
| Cold start after rescale | 22 min | 3.5 min |

## Consolidating the Pattern Library

Fourteen CEP jobs became three shared patterns with parameters, so a rule change
is one commit, not fourteen deployments.

```java
public interface RiskPatternFactory {
    String id();
    Pattern<RiskEvent, ?> build(RiskPatternConfig cfg);
    default boolean isHighCardinality() { return false; }   // drives cardinality budgets
}

public final class PatternRegistry {
    private final Map<String, RiskPatternFactory> registry = new HashMap<>();

    public static final PatternRegistry DEFAULT = new PatternRegistry()
            .register(new RapidDismantlingFactory())      // card + PIN + ATM in 10 min
            .register(new ChargebackChainFactory())       // payment -> chargeback < 72h
            .register(new MuleAccountFactory());         // many-to-many, 3 hops

    public RiskPatternFactory get(String id) {
        RiskPatternFactory f = registry.get(id);
        if (f == null) throw new IllegalArgumentException("unknown pattern " + id);
        return f;
    }
}
```

**Match cardinality is a capacity problem, not a correctness one.** A pattern
like "A B C" over 3 hops on a busy key can produce O(n^3) matches. The registry
takes `isHighCardinality` and the runner applies a per-key match budget with
side-output overflow, so a pathological day degrades into a logged sample
rather than an OOM.

## Deployment and HA on Kubernetes

```java
// A job must survive a pod eviction mid-checkpoint. Checkpoint storage is
// external and the operator restarts from the last completed checkpoint.
env.getCheckpointConfig()
   .setCheckpointStorage("s3://flink-checkpoints/risk/orders/")
   .setMinPauseBetweenCheckpoints(Duration.ofSeconds(5))
   .setTolerableFailedCheckpoints(2)
   .setCheckpointTimeout(Duration.ofMinutes(2))
   .enableUnalignedCheckpoints();     // for back-pressured jobs, unaligned
                                       // checkpoints stop the barrier from stalling

// Restart strategy: fixed delay with a cap. Exponential backoff hides a
// deterministic bug behind a long, quiet outage.
env.setRestartStrategy(RestartStrategies.fixedDelayRestart(10, Duration.ofSeconds(30)));
```

## Failure Modes and the Runbook

1. **Checkpoint timeout under back-pressure.** Symptom: `CheckpointDeclineException`
   or continuous backlog. Fix: unaligned checkpoints first; if the barrier still
   stalls, the source is slower than the sink, which is a throughput problem
   to fix honestly rather than hide with a longer timeout.
2. **State growth on one key group.** Symptom: one TaskManager OOMs while the job
   is otherwise healthy. Fix: check for an unbounded key (a `null` or default
   key collapses everything into one key group); a key-group-level metric makes
   this visible.
3. **Rescaling stalls on state redistribution.** Symptom: job runs with no output
   for minutes. Fix: `state.backend.rocksdb.local-recovery` for local-only
   recovery when the topology is unchanged; for rescaling, budget the window.
4. **Spot node preemption mid-checkpoint.** Symptom: job restarts, recovers from
   the last checkpoint. Fix: keep checkpoint storage external, and use a
   node-affinity or on-demand pool for latency-critical jobs only.
5. **Pattern match explosion.** Symptom: OOM in the CEP operator. Fix: per-key
   match budget plus side output; monitor `numMatchesEmitted` per pattern.
6. **Watermark regression after a restart.** Symptom: a gap in the output, and
   events in the gap land after the watermark. Fix: events after the watermark
   go to a late side output, reprocessed from the checkpoint in a batch pass.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Flink supports multiple levels of API (DataStream, Table API, SQL) over the
  same runtime, and its stateful operators, checkpointing, and exactly-once
  sinks are the documented foundation for production streaming.
  - Reference: (link removed)
  - Reference: (link removed)
  - Reference: https://flink.apache.org/what-is-flink/flink-applications/
- Flink's CEP library expresses patterns of events with contiguity, skipping
  strategies, and timeouts, and provides side outputs for late or partial data.
  - Reference: (link removed)
  - Reference: (link removed)
- Checkpointing and savepoints are how Flink provides fault tolerance and how
  stateful jobs are rescaled without losing in-flight work.
  - Reference: (link removed)
  - Reference: (link removed)

## Deliverables
- [ ] State-reduction refactor with the before/after metric table
- [ ] Shared pattern library replacing 14 duplicate jobs, with a cardinality budget
- [ ] Table API convention document (when SQL, when DataStream, and why)
- [ ] Checkpoint/storage/HA configuration with a failure-injection test
- [ ] Rescale runbook with measured recovery times
- [ ] Runbook for the six failure modes
- [ ] Consolidation plan with a deprecation schedule for the 14 legacy jobs
