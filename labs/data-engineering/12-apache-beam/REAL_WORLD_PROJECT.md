# Apache Beam — REAL WORLD PROJECT

## Context

A media company runs a single "audience measurement" workload across three
environments: on-prem Flink for low latency, a Spark cluster for the nightly
backfill, and a local Direct-run process for the data scientist prototyping.
The workload is implemented once in Beam, which has mostly worked — until a
recent upgrade made the three produce different numbers, and nobody could say
which was right. You own making the semantics explicit and the divergence
impossible.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Pipeline | 1 workload, 1.2B events/day, 4 branches |
| Runners | Flink (streaming, p99 < 90s), Spark (nightly batch), Direct (dev only) |
| Divergence | `avg_watch_seconds` differed 4.2% between Flink and Spark; a $2.1M ad-revenue model was off by the same ratio |
| Checkpoints | 6 min intervals on the streaming job |
| Delivery | at-least-once from the source; the sink is an API that cannot dedupe |
| Constraint | no change to the output contract; downstream models already trained on the current numbers |

## Architecture (target)

```
                       source: Kafka (30d retention) + nightly S3 replay
                                     |
                    +----------------+----------------+
                    |                                 |
             FlinkRunner (streaming)         SparkRunner (nightly)
             checkpoint 6min                 batch windowed by date
                    |                                 |
                    +----------------+----------------+
                                     |
                          convergence test suite
                          (same fixture, same expected output)
                                     |
                    output: measurement API (idempotent upsert by (event_id, branch))
```

## Key Implementation — making the divergence findable

The core fix was a **convergence test**: the same logical dataset, run through
each runner, must produce identical output. That converts "the numbers
differ" from a production mystery into a failing test.

```java
/**
 * Three sources of legitimate run-to-run difference in Beam, and only three.
 * Everything else is a bug:
 *   1. Nondeterministic ordering (no total order is defined; sort if you need one)
 *   2. Different window/trigger semantics between runners
 *   3. Different floating-point accumulation order in CombineFns
 * Fix all three explicitly and cross-runner equality becomes enforceable.
 */
public final class ConvergenceHarness {

    public record Divergence(String branch, String metric, long expected, long actual,
                             double relDiff) {}

    public List<Divergence> verify(String fixture, Map<String, PipelineResult> runs) {
        Map<String, Map<String, Double>> byRunner = new LinkedHashMap<>();
        runs.forEach((runner, res) -> byRunner.put(runner, collectMetrics(res)));

        Map<String, Double> baseline = byRunner.get("flink");
        List<Divergence> out = new ArrayList<>();
        byRunner.forEach((runner, metrics) -> metrics.forEach((metric, value) -> {
            double base = baseline.get(metric);
            if (base == null) return;
            double rel = Math.abs(value - base) / Math.max(base, 1e-9);
            if (rel > 1e-6) {                             // integer metrics: exact
                out.add(new Divergence(runner, metric, Math.round(base), Math.round(value), rel));
            }
        }));
        return out;
    }
}
```

**The 4.2% divergence had a specific cause**, and it is instructive:
`avg_watch_seconds` was computed with a `CombineFn.averageOf` whose accumulator
was a `Double`. Under Spark, the combine tree shape differed, so floating-point
addition happened in a different order — a 4.2% difference on a metric whose
inputs were 30-bit integers should be impossible, and it was not: the events
were being *deduplicated* differently.

```java
/**
 * The actual bug: deduplication used a stateful DoFn with a timer-based TTL.
 * Spark's watermark/GC behaviour differs from Flink's, so entries expired at
 * different times and some duplicate event_ids were counted twice.
 *
 * Fix: make deduplication an explicit, ordered operation with a deterministic
 * expiry, not a side effect of state GC.
 */
public class DeduplicateByEventId extends DoFn<Event, Event> {
    @StateId("seen") private transient SetState<String> seen;
    @StateId("lastSweep") private transient ValueState<Instant> lastSweep;
    @TimerId("sweep") private transient TimerSpec sweep;

    @ProcessElement
    public void process(@Element Event e,
                        @Timestamp Instant ts,
                        @TimerId("sweep") Timer t,
                        OutputReceiver<Event> out) {
        if (!seen.add(e.eventId())) return;            // duplicate: deterministic drop
        // Sweep on a fixed cadence derived from element time, identical everywhere.
        Instant next = lastSweep.read() == null ? ts.plus(Duration.ofHours(1))
                                                : lastSweep.read().plus(Duration.ofHours(1));
        lastSweep.write(next);
        t.set(next);
        out.output(e);
    }

    @OnTimer("sweep")
    public void sweep() {
        Instant now = lastSweep.read();
        if (now == null) return;
        seen.clear();                                  // hourly, element-time driven
        lastSweep.write(now.plus(Duration.ofHours(1)));
    }
}
```

## Semantics Declared, Not Assumed

```java
/**
 * Delivery contract, written once and asserted per runner:
 *
 *  source        : at-least-once, 30d retention, replayable
 *  transform     : deterministic; integer metrics only (no Float accumulators)
 *  dedup         : explicit, hourly element-time sweep
 *  sink          : idempotent upsert keyed by (branch, event_id)
 *  exactly-once  : NOT claimed. Achieved instead by end-to-end idempotency.
 *
 * This is the honest position: claiming exactly-once without a transactional
 * sink is how a 4.2% divergence ships to a revenue model.
 */
public interface MeasurementContract {
    String SOURCE_DELIVERY = "at-least-once";
    String DEDUP_GRANULARITY = "hourly (element time)";
    String SINK_STRATEGY = "idempotent upsert (branch, event_id)";
    boolean EXACTLY_ONCE = false;
}
```

## Runner Choice, Documented

| Branch | Runner | Why not the others |
|---|---|---|
| Streaming audience counts | Flink | checkpointed state, per-key timers, low latency |
| Nightly 30d backfill | Spark | batch, high throughput, no state; Beam's model is a good fit for a date-partitioned job |
| Ad-hoc validation | Direct | debuggability, single-process, small fixtures only — never a production path |

The lesson the team wrote down: **Beam earns its cost when the same logic must
run in more than one execution mode with identical semantics.** Where only one
mode exists, the engine's own API is usually less code and easier to debug.

## Failure Modes and the Runbook

1. **Runner upgrade changes output.** Symptom: nightly numbers differ from
   streaming by a fraction of a percent. Fix: the convergence test suite runs
   on every upgrade, against a golden fixture, in CI.
2. **Checkpoint too infrequent for the state size.** Symptom: after a failure,
   replay is slow and a downstream dedup window has expired. Fix: checkpoint
   interval derived from state size and replay tolerance, measured per branch.
3. **State grows unboundedly in the dedup DoFn.** Symptom: OOM in a TaskManager.
   Fix: the explicit sweep above; alert on state size per key group.
4. **Source retention shorter than replay time.** Symptom: a recovery cannot
   catch up. Fix: retention >= worst-case recovery window, asserted in a
   pre-deployment check.
5. **Beam version skew between environments.** Symptom: works on the cluster,
   fails locally. Fix: pin one Beam version, ship the runner jars explicitly,
   and containerize the Direct-runner "dev" path so it cannot drift.
6. **Window semantics differ across runners for a custom trigger.** Symptom:
   partial results emitted on one runner only. Fix: avoid runner-specific
   trigger extensions; use standard triggers and a side-output late-data path.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Apache Beam provides a unified model for batch and streaming data processing
  with language SDKs and multiple runners, so one pipeline can execute on
  different backends.
  - Reference: https://beam.apache.org/documentation/
  - Reference: (link removed)
  - Reference: https://beam.apache.org/documentation/runners/capability-matrix/
- Beam's execution model includes windows, triggers, and state/timers, and the
  runner capability matrix documents which features each backend supports.
  - Reference: https://beam.apache.org/documentation/runtime/model/
  - Reference: (link removed)

## Deliverables
- [ ] Convergence test suite (one fixture, three runners, exact equality)
- [ ] Written delivery contract, including the explicit no-exactly-once decision
- [ ] Deterministic dedup DoFn replacing timer-based TTL expiry
- [ ] Runner selection table with reasoning per branch
- [ ] Checkpoint interval policy derived from state size and replay tolerance
- [ ] Runbook for the six failure modes
- [ ] Postmortem of the 4.2% divergence with the root cause chain
