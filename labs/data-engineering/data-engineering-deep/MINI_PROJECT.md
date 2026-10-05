# data-engineering-deep — MINI PROJECT

## Project: End-to-End Streaming Warehouse with a Proof of Correctness

One project that exercises all ten models: streaming ingest with event time, a
stateful aggregation, a table-format sink, an hourly reconciliation, a
freshness SLO, a cost model, and a crash-recovery test.

### Scope

- **Ingest**: NDJSON event tail simulating Kafka, with configurable lateness
  and a "bad producer" mode that flushes in bursts.
- **Transform**: event-time session windows, a keyed stateful funnel, and one
  point-in-time-correct join against a reference dimension.
- **Sink**: a Delta-style table with a MERGE scoped by partition, plus a
  two-phase-commit mode.
- **Reconciliation**: hourly, event-time bounded, against a batch recomputation.
- **Serving**: a small HTTP endpoint reading the table, with a staleness badge.
- **Ops**: a freshness SLO, an error budget, a cost model, a runbook.

### Architecture

```
events.ndjson (tail; 3 lateness profiles)
   |
[StreamJob]
   |-- watermark: per-source out-of-orderness + idleness
   |-- keyBy(user) -> session window (30s gap) -> sessions
   |-- keyBy(user) -> stateful funnel (stage timers, 10m timeout)
   |-- point-in-time join to dim_user (versioned, as-of event time)
   v
[TableSink]  MERGE scoped by (hour, tenant)  ->  fact_events
   |                                        \-> _changes audit
[Reconciler] hourly: streaming vs batch recompute, diff by (metric, tenant, hour)
   |
[ServingApi] reads the table, reports freshness + maturity
   |
[SLO] freshness 2h, error budget 99.5%; burn rate routes page/ticket/silent
```

### Implementation — the stream job

```java
public final class StreamJob {
    public static void main(String[] args) throws Exception {
        Config cfg = Config.fromArgs(args);

        StreamExecutionEnvironment env =
                StreamExecutionEnvironment.getExecutionEnvironment();
        env.enableCheckpointing(30_000, CheckpointingMode.EXACTLY_ONCE);
        env.getCheckpointConfig().setCheckpointStorage(cfg.checkpointPath());
        env.getCheckpointConfig().setCheckpointTimeout(Duration.ofMinutes(5));
        env.setStateBackend(new EmbeddedRocksDBStateBackend(true));  // incremental

        DataStream<Event> events = new NdjsonTailSource(cfg.input())
                .assignTimestampsAndWatermarks(
                        WatermarkStrategy.<Event>forBoundedOutOfOrderness(cfg.latency())
                                .withTimestampAssigner((e, ts) -> e.ts().toEpochMilli())
                                .withIdleness(Duration.ofSeconds(30)));

        // Model 5: partitioning. keyBy(user) gives per-user ordering and
        // parallelism; a bad key collapses the job onto one key group.
        SingleOutputStreamOperator<Session> sessions = events
                .keyBy(Event::userId)
                .window(new SessionWindowsGap(Time.milliseconds(30_000)))
                .process(new SessionBuilder())
                .uid("sessions");                                  // uid anchors state

        SingleOutputStreamOperator<FunnelProgress> funnel = events
                .keyBy(Event::userId)
                .process(new Funnel(STAGE_TIMEOUT_MS))
                .uid("funnel");

        // Model 7: point-in-time correctness. The dimension is versioned, and
        // the join uses the version valid at the EVENT time, not at processing time.
        SingleOutputStreamOperator<Enriched> enriched = events
                .keyBy(Event::userId)
                .connect(versionedDimSource(cfg.dimPath()))
                .process(new PointInTimeJoin())
                .uid("pit-join");

        // Model 3: idempotent sink. Keyed MERGE on the natural key, scoped by
        // (hour, tenant) so the affected file set is knowable before we start.
        new ScopedMergeSink(cfg.tablePath(), List.of("hour", "tenant"))
                .setParallelism(cfg.sinkParallelism())
                .invoke(new WindowedRecord())

        env.execute("streaming-warehouse");
    }
}
```

### The funnel, with a state bound (Model 2)

```java
public class Funnel extends KeyedProcessFunction<String, Event, FunnelProgress> {
    private static final List<String> STAGES =
            List.of("view", "add_to_cart", "checkout", "purchase");

    private transient MapState<Long, StageReached> reached;   // ts -> stages
    private transient ValueState<Long> lastAdvanceTs;

    @ProcessElement
    public void processElement(Event e, Context ctx, Collector<FunnelProgress> out)
            throws Exception {
        int s = STAGES.indexOf(e.type());
        if (s < 0) return;

        // Model 5: no "furthest" unbounded state. We keep only the current
        // funnel with a TTL, so memory is O(1) per user rather than O(events).
        StageReached cur = reached.get(e.ts() / 60_000);
        if (cur == null) cur = new StageReached(0, 0.0);
        if (s <= cur.furthest()) return;                          // monotonic

        cur = new StageReached(s, cur.value() + e.value());
        reached.put(e.ts() / 60_000, cur);
        lastAdvanceTs.update(e.ts());

        // Model 2: an explicit expiry. Without it, a user who visits once a
        // year keeps state for a year.
        ctx.timerService().registerEventTimeTimer(e.ts() + FUNNEL_TTL_MS);

        out.collect(new FunnelProgress(e.userId(), e.tenant(), e.type(),
                s, cur.value(), s == STAGES.size() - 1, e.ts()));
    }

    @OnTimer
    public void onExpire(@Timestamp Instant ts, OutputCollector<FunnelProgress> out)
            throws Exception {
        reached.clear();
    }
}
```

### The scoped, idempotent sink (Models 3 and 7)

```java
public final class ScopedMergeSink extends TwoPhaseCommitSinkFunction<WindowedRecord, Tx> {

    private final Table table;
    private final List<String> scopeColumns;   // ["hour", "tenant"]

    /**
     * Before touching anything, state which partitions this MERGE can reach.
     * If that scope is a large fraction of the table, refuse: an unbounded
     * MERGE rewrites the table, which is a six-hour job and a lock on the
     * hourly refresh.
     */
    @Override public Tx beginTransaction() throws Exception {
        Set<String> scope = new HashSet<>();
        long bytes = 0;
        for (WindowedRecord r : buffer) {
            scope.add(scopeKey(r));
            bytes += table.bytesForPartition(scopeKey(r));
        }
        if (table.totalBytes() > 0 && bytes / (double) table.totalBytes() > MAX_SCOPE_FRACTION) {
            throw new ScopeTooLargeException(
                    "MERGE scope is " + bytes + " bytes of " + table.totalBytes()
                    + "; widen the partitioning or aggregate earlier");
        }
        return new Tx(txnIdSeq.incrementAndGet(), scope);
    }

    @Override public void invoke(Tx tx, WindowedRecord r, Context ctx) throws Exception {
        // Idempotency by natural key + monotonic hour. Re-delivery updates;
        // it never inserts a second row.
        table.stageMerge(tx.id(), r.businessKey(), r.hour(), r.payload());
    }

    @Override public void commitTransaction(Tx tx) throws Exception {
        table.promoteStaged(tx.id(), scopeColumns);   // single atomic transaction
    }

    @Override public void abortTransaction(Tx tx) throws Exception {
        table.discardStaged(tx.id());
    }

    private String scopeKey(WindowedRecord r) {
        return r.hour() + "/" + r.tenant();
    }
}
```

### Reconciliation against a batch recomputation (Model 7)

```java
public final class Reconciler {
    /**
     * The event-time boundary is the whole point. Comparing a stream that has
     * seen 55 minutes of an hour against a batch that has seen 60 produces a
     * false alarm every run.
     */
    public List<Diff> run(long hoursBack, Instant now) {
        List<Diff> out = new ArrayList<>();
        for (long h = 1; h <= hoursBack; h++) {
            long hourEnd = now.atZone(ZoneOffset.UTC).truncatedTo(ChronoUnit.HOURS)
                    .minusHours(h).toInstant().toEpochMilli();
            long hourStart = hourEnd - 3_600_000L;
            if (now.isBefore(Instant.ofEpochMilli(hourEnd).plus(REQUIRED_QUIET))) continue;

            for (String tenant : tenants()) {
                double streaming = table.sum("revenue", tenant, hourStart, hourEnd);
                double batch     = batchRecompute(tenant, hourStart, hourEnd);
                double diff = batch == 0 ? 0 : 100 * (streaming - batch) / batch;
                out.add(new Diff("revenue", tenant, hourStart, streaming, batch,
                        diff, Math.abs(diff) <= TOLERANCE_PCT ? Verdict.OK : Verdict.BREACH));
            }
        }
        return out;
    }
}
```

### SLO and error budget (Model 9)

```java
public final class SloMonitor {
    static final Duration FRESHNESS_TARGET = Duration.ofHours(2);
    static final double TARGET_AVAILABILITY = 0.995;      // 30-day window

    public enum Delivery { PAGE, TICKET, SILENT }

    /** Burn rate = budget consumed per hour, normalised. 14.4x = 1% in 1 hour. */
    public Delivery route(boolean breach, double burnRate, boolean knownIssue) {
        if (knownIssue) { logSuppressed(); return Delivery.SILENT; }
        if (!breach) return Delivery.SILENT;
        if (burnRate > 14) return Delivery.PAGE;
        if (burnRate > 6) return Delivery.TICKET;
        return Delivery.SILENT;
    }

    public double remainingBudget(Instant windowStart, List<Diff> diffs) {
        long bad = diffs.stream().filter(d -> d.verdict() == Verdict.BREACH).count();
        return 1.0 - (double) bad / Math.max(1, diffs.size());
    }
}
```

### The crash-recovery test (Models 2 and 3)

```
1. Run the job to steady state. Record the committed total.
2. kill -9 the task process mid-window.
3. Assert: the job restarts, recovers from the last completed checkpoint,
   and the committed total afterwards equals
       (sum before crash) + (sum of events after the checkpoint offset)
   with no duplicates and no gaps.
4. Assert: the staging table is empty (aborted transactions discarded) and no
   promoted transaction is partial.
5. Repeat with the kill happening between promoteStaged and the next checkpoint,
   which is the window where a naive sink double-counts.
```

Step 5 is the one that finds real bugs. Include it.

### Cost model (Model 8)

```java
public record CostModel(long eventsPerDay, int bytesPerEvent, double replayFactor,
                        String storageRate, String scanRate) {
    public double dailyStorageUsd() {
        return eventsPerDay * bytesPerEvent * replayFactor / 1e12 * storageRate;
    }
    public double costPerQuery(double bytesScanned) {
        return bytesScanned / 1e12 * scanRate;
    }
    /** The number that should drive design: cost of ONE dashboard refresh. */
    public double dashboardRefreshCost(int panels, double bytesPerPanel) {
        return panels * costPerQuery(bytesPerPanel);
    }
}
```

Fill in real numbers and write down which cost line is actually movable for
this workload. For a 2PB/day ingest with 2h freshness, it is almost never
storage.

### Stretch

- Add a replay mode: reset the source offset and verify the table converges to
  the same state (tests idempotency at a scale the unit test cannot).
- Add a bad-producer mode that flushes a 20-minute backlog at once, and measure
  correction rate and state size.
- Add a point-in-time leak test: a feature version dated after the label must
  never appear in the training set.

## Deliverables

- [ ] Stream job with event time, idleness, per-source lateness, and stable uids
- [ ] State-bounded funnel with an explicit TTL and a state-size measurement
- [ ] Scoped, idempotent, two-phase-commit sink that refuses an oversized MERGE
- [ ] Point-in-time-correct dimension join with a leak test
- [ ] Hourly, event-time-bounded reconciliation with a stated tolerance
- [ ] Freshness SLO with burn-rate routing and a suppressed-alert log
- [ ] Crash-recovery test including the promote/checkpoint window
- [ ] Cost model with the movable line identified
- [ ] Replay-mode convergence test
- [ ] Runbook covering: watermark stall, correction storm, state growth,
      scope refusal, checkpoint failure, and reconciliation breach
