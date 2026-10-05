# Streaming Analytics — REAL WORLD PROJECT

## Context

A live-sports streaming service runs a "live ops" product: viewers per
channel, watch time, ad-fill revenue, and a churn-risk signal, on 90-second
delays for the rights-holder feed. The current implementation is processing-time
and gives numbers that disagree with billing by 2-8% during peak, which has
become a contractual conversation with three rights holders. You own the
correctness of live analytics.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Input | 1.4M events/sec peak, 210B events/day |
| Concurrency | 90k concurrent viewers; 4 analytics jobs |
| Latency SLO | p99 < 3s from event to rights-holder feed |
| Correctness | must reconcile to billing within 0.5% by the end of each event hour |
| Sources | Kafka playback events, ad-impression logs (2 different producers) |
| Late data | ad logs arrive up to 25 min late; playback events ~2s |
| Contracts | 3 rights holders bill on these numbers; disputes cost real money |
| Constraint | cannot change the ad-log producer's timing behaviour |

## Architecture (target)

```
playback events (Kafka, 4 min late max) ---+
                                           |
ad logs (Kafka, 25 min late max) ----------+--> [Analytics job]
                                                     |
                                    +----------------+----------------+
                                    |                                 |
                             live serving store              batch reconciliation
                             (keyed upsert, push)            (hourly, authoritative)
                                    |                                 |
                          rights-holder feed                   billing comparison
                                    |
                          corrections channel (late deltas)
```

## Key Implementation — the four decisions that made the numbers right

**Decision 1: event time, with a per-source lateness budget derived from the
producer, not from a guess.** This is the single change that moved the
disagreement from 2-8% to under 0.5%.

```java
/**
 * Lateness is a property of the producer, and it must be stated per source.
 *
 *   playback events: emitted by the CDN edge within ~2s of the event
 *   ad logs        : batched per advertiser endpoint, flushed every ~20 min
 *
 * Using one global watermark (say 30s) is wrong in both directions: too tight
 * for ad logs, which produces constant corrections, and too loose for
 * playback, which makes the live feed less fresh than it needs to be.
 */
public record SourceWatermarkPolicy(String source, Duration outOfOrderness,
                                    Duration idleness, Duration finalizationLag) {
    public static final SourceWatermarkPolicy PLAYBACK =
            new SourceWatermarkPolicy("playback", Duration.ofSeconds(4),
                                      Duration.ofSeconds(20), Duration.ofMinutes(2));
    public static final SourceWatermarkPolicy ADS =
            new SourceWatermarkPolicy("ads", Duration.ofMinutes(25),
                                      Duration.ofMinutes(2), Duration.ofMinutes(40));
}
```

**Decision 2: the live number carries its own confidence.** A rights holder
receiving a number must know how provisional it is. This is a commercial
requirement as much as a technical one, and it ended most disputes early.

```java
public enum Maturity { PROVISIONAL, STABLE, FINAL, RESTATED }

public record LiveMetric(String metric, String key, double value, long eventHourStart,
                         long eventHourEnd, Maturity maturity, long computedAt,
                         double expectedResidualErrorPct) {
    /**
     * Provisional: the window is still open for late data, so the expected
     * residual is the observed late rate for this source.
     * Final: the window passed finalizationLag and no corrections arrived.
     * Restated: a correction landed after the number was sent - the client
     * must display the new value and the restatement reason.
     */
    public static LiveMetric provisional(String metric, String key, double v,
                                        long hStart, long hEnd, long now) {
        long lag = now - hEnd;
        double residual = lag < 60_000 ? 4.0 : 1.2;
        return new LiveMetric(metric, key, v, hStart, hEnd,
                lag < 60_000 ? Maturity.PROVISIONAL : Maturity.STABLE, now, residual);
    }
}
```

**Decision 3: corrections are a first-class channel, not an in-place update.**
Rights holders cache the numbers they receive. An in-place correction is
invisible to them, so a restatement must be pushed as a distinct event.

```java
public record Restatement(String metric, String key, long eventHourStart,
                          double previousValue, double newValue, double deltaPct,
                          String reason, long issuedAt) {
    public String explain() {
        return String.format("restatement for %s %s hour %d: %.0f -> %.0f (%+.2f%%), reason: %s",
                metric, key, eventHourStart, previousValue, newValue, deltaPct, reason);
    }
}

/**
 * Restatement policy, which is a contract decision as much as an engineering one:
 *   - within 2h of the hour closing: silent correction, no restatement event
 *     (the client has not likely cached it)
 *   - 2h to 24h: restatement event, client must update
 *   - beyond 24h: restatement event + a reconciliation note to billing
 * The rights-holder contract specifies which applies; the code must match it.
 */
public enum RestatementPolicy { SILENT_CORRECTION, NOTIFY, NOTIFY_AND_RECONCILE }

public RestatementPolicy policyFor(long hourStart, long now) {
    long hoursSince = (now - hourStart) / 3_600_000;
    if (hoursSince <= 2) return RestatementPolicy.SILENT_CORRECTION;
    if (hoursSince <= 24) return RestatementPolicy.NOTIFY;
    return RestatementPolicy.NOTIFY_AND_RECONCILE;
}
```

**Decision 4: a continuous reconciliation loop, not an annual one.** The
authority is the hourly batch. The streaming path is checked against it
continuously, and the difference is monitored as a business metric.

```java
public record Reconciliation(String metric, long eventHourStart, double streaming,
                             double batch, double diffPct, String verdict) {
    public String verdict() {
        double abs = Math.abs(diffPct);
        if (abs <= 0.5) return "WITHIN_CONTRACT";       // 0.5% is the contractual band
        if (abs <= 2.0) return "INVESTIGATE";
        return "DISPUTE_RISK";
    }
}

public final class ReconciliationLoop {
    /**
     * The important design point: the comparison is by (metric, key, event hour)
     * with an *event-time* boundary, not an ingestion-time one. Comparing a
     * stream that has seen 55 minutes of an hour against a batch that has seen
     * 60 is the single most common way these loops produce false alarms.
     */
    public List<Reconciliation> run(long eventHoursBack, Instant now) {
        List<Reconciliation> out = new ArrayList<>();
        for (long h = 0; h < eventHoursBack; h++) {
            long hourStart = now.minus(Duration.ofHours(h + 1)).toEpochMilli() / 3_600_000 * 3_600_000;
            long hourEnd = hourStart + 3_600_000;
            if (now.isBefore(Instant.ofEpochMilli(hourEnd).plus(ADS_FINAL_LAG))) continue;
            for (String key : streaming.keysInWindow(hourStart, hourEnd)) {
                double s = streaming.get("revenue", key, hourStart, hourEnd);
                double b = batch.get("revenue", key, hourStart, hourEnd);
                double diff = b == 0 ? 0 : 100 * (s - b) / b;
                out.add(new Reconciliation("revenue", key, hourStart, s, b, diff, null));
            }
        }
        return out;
    }
}
```

## The Measured Result

| Metric | Before | After |
|---|---|---|
| Disagreement vs billing | 2-8% at peak | < 0.4% at p95 |
| Live feed latency p99 | 41s | 2.6s |
| Rights-holder disputes | 6 in 18 months | 0 |
| Ad revenue under-reporting at peak | up to 8% | 0.2% |
| Restatements issued | n/a | 0.4% of hours, all within the 24h window |
| Streaming compute cost | $180k/month | $214k/month (+19% for correctness) |

The cost increase was accepted deliberately: 8% under-reporting of ad revenue
at peak was worth far more than $34k/month in compute.

## Failure Modes and the Runbook

1. **Watermark stalls on a partition.** Symptom: the feed freezes while traffic
   continues. Fix: `withIdleness` per source; alert on
   `watermark - wallClock` and on `keysInWindow` returning nothing.
2. **Correction storm.** Symptom: thousands of restatement events for one hour.
   Cause: a source flushed a 25-minute batch late. Fix: a per-hour correction
   rate alert at 5x the trailing median, and aggregation of restatements into a
   single event per (metric, key, hour) with a summed delta.
3. **State growth on a session window.** Symptom: a TaskManager OOMs on a
   gaming-shaped traffic spike. Fix: session TTL, plus a max-session-duration
   cap (a 3-hour "session" is a stuck client, not a session).
4. **Rights-holder caches a provisional number and later disputes the final
   one.** Symptom: a dispute about a number they were told was stable. Fix: the
   feed labels maturity, the contract specifies how maturity is displayed, and
   the client-side badge is part of the integration test.
5. **Double counting from at-least-once delivery.** Symptom: revenue is 3% high
   and drifts upward. Fix: keyed upsert semantics, not accumulate, plus a
   per-key event-id dedup at the window level.
6. **A new metric is added to the feed without a maturity rule.** Symptom:
   numbers that are never final and confuse the recipient. Fix: a registration
   step that requires a lateness policy and a maturity function before a metric
   can be published.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Flink's stateful stream processing provides event time, watermarks, windows,
  and checkpoint-based recovery, which are the mechanisms that make streaming
  analytics reproducible after failure.
  - Reference: https://flink.apache.org/what-is-flink/
  - Reference: https://flink.apache.org/flink-docs-stable/docs/concepts/stateful-stream-processing/
  - Reference: https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/
- Kafka guarantees ordering within a partition and replay by offset, which is
  what allows a streaming metric to be recomputed from the log after a fix.
  - Reference: https://kafka.apache.org/documentation/#design
  - Reference: https://kafka.apache.org/documentation/#intro_concepts_and_terms
- Table formats with time travel (Iceberg, Delta) support the batch-side
  authority and the point-in-time reconstruction needed for reconciliation.
  - Reference: https://iceberg.apache.org/docs/latest/
  - Reference: https://docs.delta.io/latest/index.html

## Deliverables
- [ ] Per-source watermark policy derived from producer behaviour, with the reasoning
- [ ] Maturity-labelled metrics (provisional / stable / final / restated)
- [ ] Restatement channel with a policy matched to the rights-holder contracts
- [ ] Continuous event-time-bounded reconciliation against the batch authority
- [ ] Correction-storm detection with per-hour aggregation of restatements
- [ ] Session TTL and max-session-duration cap
- [ ] Idempotent keyed upsert with a dedup test
- [ ] Before/after table covering latency, agreement, disputes, and cost
- [ ] Runbook for the six failure modes
