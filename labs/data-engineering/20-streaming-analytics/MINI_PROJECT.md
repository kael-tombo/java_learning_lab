# Streaming Analytics — MINI PROJECT

## Project: Live Metrics Pipeline with a Push Served Dashboard

Events in, event-time windows out, a WebSocket dashboard, and an explicit
late-data correction path. Pure Java plus a small HTTP/WebSocket server.

### Scope
- Ingest: NDJSON events from a file tailer, simulating a Kafka consumer.
- Job A `traffic`: per-key event-time tumbling windows (1s) + session windows.
- Job B `funnel`: stage transitions with a timeout per stage.
- Serving: `AggregateStore` with push updates over WebSocket.
- Corrections: late events produce a `Correction` sent to the client, which
  updates the displayed value and shows a "corrected" marker.
- Metrics: end-to-end latency, lag, late rate, correction count.

### Architecture

```
events.ndjson (tail)
   |
[EventTimePipeline]
   |-- watermark strategy: out-of-orderness 2s, idleness 5s
   |-- window(TUMBLING 1s)   -> per-key counts
   |-- window(SESSION 30s)   -> sessions
   |-- funnel(state + timer) -> conversions
   v
[AggregateStore]  (bounded state, TTL 10 min)
   |
[WebSocketPush] -> dashboard (counts, sessions, conversion rate, staleness badge)
   v
late events --> [CorrectionQueue] --> client applies the delta, marks corrected
```

### Implementation

```java
public final class EventTimePipeline {
    public static void main(String[] args) throws Exception {
        // 1. source
        EventSource source = new FileTailSource(Path.of("data/events.ndjson"));

        // 2. event time with an explicit out-of-orderness assumption and
        //    idleness, so a stalled partition cannot freeze the global watermark
        WatermarkStrategy<Event> wm = WatermarkStrategy
                .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(2))
                .withTimestampAssigner((e, ts) -> e.ts().toEpochMilli())
                .withIdleness(Duration.ofSeconds(5));

        // 3. windowed aggregation
        SingleOutputStreamOperator<WindowCount> perSecond = source.stream(wm)
                .keyBy(Event::channel)
                .window(TumblingEventTimeWindows.of(Duration.ofSeconds(1)))
                .aggregate(new CountAgg(), new AddWindowMetadata());
        perSecond.name("traffic-per-second").uid("traffic");

        // 4. sessions
        SingleOutputStreamOperator<Session> sessions = source.stream(wm)
                .keyBy(Event::userId)
                .window(new SessionWindowsGap(Time.milliseconds(30_000)))
                .process(new SessionBuilder());

        // 5. serving: push, not pull
        AggregateStore store = new AggregateStore(Duration.ofMinutes(10));
        perSecond.addSink(new PushSink(store, new WebSocketBroadcaster("ws://localhost:8090/ws")));
        sessions.addSink(new PushSink(store, new WebSocketBroadcaster("ws://localhost:8090/ws")));

        env.execute("live-metrics");
    }
}
```

### Correct late-data handling with visible correction

```java
public record Correction(long windowStart, long windowEnd, String key, String metric,
                         double previousValue, double delta, double newValue,
                         long eventTime, long correctionTime) {}

public final class WindowSink {
    private final Map<WindowKey, Double> current = new HashMap<>();
    private final Duration allowedLateness = Duration.ofSeconds(30);
    private final OutputTag<Correction> lateTag = new OutputTag<>("late") {};

    public void process(WindowCount wc, OutputTag<Correction> late, Collector<Update> out) {
        WindowKey key = new WindowKey(wc.key(), wc.windowStart());
        double previous = current.getOrDefault(key, 0.0);
        current.merge(key, wc.count(), Double::sum);
        out.collect(new Update(key, current.get(key), late.isPresent()
                ? "corrected" : "final"));
    }

    /**
     * Two distinct cases, and conflating them is the classic bug:
     *   - the window already fired because time advanced (watermark passed):
     *     the value is WRONG on screen and must be corrected
     *   - the window has not fired yet: the value is simply early, no correction
     */
    public void onLate(Event e, long windowStart, long windowEnd) {
        long now = System.currentTimeMillis();
        long elapsed = now - windowEnd;
        if (elapsed > allowedLateness.toMillis()) {
            // Too late to correct: route to a batch reconciliation instead of
            // emitting a correction nobody will reconcile.
            reconciliationQueue.enqueue(e, windowStart, windowEnd);
            return;
        }
        corrections.emit(new Correction(windowStart, windowEnd, e.channel(), "count",
                current.getOrDefault(new WindowKey(e.channel(), windowStart), 0.0), 1,
                current.getOrDefault(new WindowKey(e.channel(), windowStart), 0.0) + 1,
                e.ts(), now));
    }
}
```

### The client must know how stale a number is

```java
public record DashboardUpdate(String key, String metric, double value, long windowEnd,
                              Instant computedAt, String status,
                              Duration stalenessAtSend) {
    public String stalenessBadge() {
        return switch (status) {
            case "corrected" -> "corrected at " + computedAt;
            case "partial"   -> "partial (" + stalenessAtSend.toSeconds() + "s behind)";
            default          -> "final";
        };
    }
}
```

### Funnel with per-stage timers

```java
public class Funnel extends KeyedProcessFunction<String, Event, StageProgress> {
    private static final List<String> STAGES =
            List.of("view", "add_to_cart", "checkout", "purchase");
    private transient MapState<Integer, Long> stageEntered;   // stage -> ts
    private transient ValueState<Integer> furthest;

    @ProcessElement
    public void processElement(Event e, Context ctx, Collector<StageProgress> out) throws Exception {
        int s = STAGES.indexOf(e.type());
        if (s < 0) return;
        if (furthest.value() == null) furthest.update(0);

        // Only advance forward: a user cannot un-purchase
        if (s <= furthest.value()) return;
        stageEntered.put(s, e.ts());
        furthest.update(s);

        long entered = stageEntered.get(s);
        ctx.timerService().registerEventTimeTimer(entered + STAGE_TIMEOUT_MS);

        out.collect(new StageProgress(e.userId(), e.type(), e.ts(),
                e.value() == null ? 0 : e.value(), reachedFinal = s == STAGES.size() - 1));
    }

    /** A stalled funnel is a real signal: emit a partial so the dashboard can show it. */
    @OnTimer
    public void onTimeout(@Timestamp Instant ts, OutputCollector<StageProgress> out) {
        int f = furthest.value() == null ? 0 : furthest.value();
        out.collect(new StageProgress("timeout", STAGES.get(f), ts, 0, false, partial = true));
    }
}
```

### Test It

```java
@Test void lateEventProducesCorrectionNotOverwrite() {
    WindowSink sink = new WindowSink(Duration.ofSeconds(30));
    List<Update> updates = new ArrayList<>();
    sink.process(window("eu", t0, 100, 10), out(updates));
    sink.onLate(event("eu", t0 + 2500, "click"), t0, t0 + 1000);
    assertEquals(1, corrections.size());
    assertEquals(11.0, corrections.get(0).newValue());
    assertEquals("corrected", updates.get(0).status());
}

@Test void idempotentChannelProducesNoDoubleCount() {
    // Same event delivered twice (at-least-once) must count once
    store.upsert(windowKey, 1.0);
    store.upsert(windowKey, 1.0);
    assertEquals(1.0, store.get(windowKey));   // keyed upsert, not accumulate
}
```

### Stretch
- Add a session-window session count and compare to the batch number.
- Measure lag and the correction rate; add a dashboard panel for both.
- Add a "reconciliation" panel that diffs the streaming total against a batch run.

## Deliverables
- [ ] Event-time pipeline with explicit out-of-orderness and idleness
- [ ] Two window types (tumbling, session) plus a stateful funnel with timers
- [ ] WebSocket push serving with a staleness badge in every payload
- [ ] Correction channel for late data, with a too-late routing to reconciliation
- [ ] Latency, lag, late-rate, and correction-rate metrics
- [ ] Tests for late data, idempotency, and staleness reporting
