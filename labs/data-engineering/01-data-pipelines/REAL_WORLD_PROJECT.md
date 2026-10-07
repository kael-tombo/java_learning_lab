# Data Pipelines — REAL WORLD PROJECT

## Context

A subscription retailer moved 14 event sources (orders, refunds, subscriptions,
web events, warehouse ticks, payment webhooks) into one revenue platform. The
old system was a chain of cron scripts writing CSVs into a shared NFS folder.
Nobody could answer "how much revenue did we book on Tuesday?" with confidence.

Your job: design the pipeline layer that replaces it, and defend the design.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Ingest rate | ~40k events/sec peak, ~2M/sec on a promo day |
| Latency SLO | < 60s end-to-end for revenue, daily is unacceptable |
| Throughput day | ~1.5B raw events retained 13 months |
| Ordering | per-`order_id` required; global order not required |
| Team | 4 engineers, no dedicated platform team |
| Compliance | GDPR deletes must propagate to all derived data |

## Architecture

```
producers -> Kafka (3 topics, 48 partitions)
              |
        CDC / API gateway
              |
   +----------+-----------+--------------------+
   |          |           |                    |
 stream     stream      batch (Airflow)      reverse CDC
 (Flink)    (Flink)     (Spark / SQL)        (apply deletes to OLTP)
 revenue    fraud         marts                 |
   |          |            |                    |
 warehouse <- Delta/Iceberg lakehouse tables <-+
   |
 dbt / semantic layer -> dashboards, finance close
```

## Key Implementation — transactional sink

The single most important decision: the lakehouse sink is idempotent and
partitioned by business date, so replay is always safe.

```java
public class LakehouseSink {
    private final Table table;            // Delta or Iceberg
    private final Map<LocalDate, Long> writtenCounts = new HashMap<>();

    public void write(RevenueEvent e) {
        // Merge on the natural key so a replay updates, never duplicates.
        table.merge("date", e.businessDate())
             .whenMatchedUpdateAll(e.asRow())
             .whenNotMatchedInsertAll(e.asRow())
             .execute();
    }
}
```

## Failure Modes and the Runbook

1. **Consumer group rebalance storm** after a deploy. Symptom: lag sawtooth,
   `rebalance.count` spiking. Fix: increase `max.poll.interval.ms`, move
   processing off the poll thread, static membership to avoid rebalances.
2. **Upstream schema change** (new nullable column). Symptom: deserialization
   errors climbing. Fix: schema registry compatibility check in CI; a
   `BACKWARD` break is a deploy blocker, not a runtime surprise.
3. **Late data** for a closed day. Symptom: yesterday's revenue changes. Fix:
   reconciliation job re-aggregates a rolling 3-day window and writes a
   delta row; dashboards show "as of" timestamps so finance trusts the number.
4. **GDPR erasure request**. Fix: a tombstone event drives deletes in every
   derived table; a nightly job proves no orphaned PII remains.
5. **Promo-day overload**. Fix: autoscale partitions ahead of the event, cap
   downstream concurrency, and shed non-critical enrichment first.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Kafka delivers each partition in order and lets you replay by resetting
  offsets; all consumer state is external to the broker. Design for at-least-once
  and make the sink idempotent.
  - Reference: https://kafka.apache.org/documentation/
  - Reference: https://kafka.apache.org/documentation/#design
- Apache Flink checkpoints state to a durable backend and restores from the
  last completed checkpoint after failure, which is what makes long-running
  streaming state survivable.
  - Reference: https://flink.apache.org/what-is-flink/
  - Reference: (link removed)
- Airflow is a workflow orchestrator: the scheduler runs tasks, not data
  movement, and correctness of the DAG comes from defining dependencies and
  handling retries/idempotency yourself.
  - Reference: https://airflow.apache.org/docs/apache-airflow/stable/index.html

## Deliverables
- [ ] Architecture decision record for batch-vs-streaming per data product
- [ ] Idempotent sink with a replay test
- [ ] Latency + lag SLO dashboard spec
- [ ] On-call runbook covering the five failure modes above
- [ ] Backfill procedure for a 30-day restatement, with a reconciliation query
