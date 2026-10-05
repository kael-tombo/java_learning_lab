# Lab 13 — Exercises: Kafka Consumer Lag

## Part A — Observe (1–15)
1. `kafka-consumer-groups.sh --bootstrap-server K --describe --group orders` — record LAG per partition.
2. Identify hot partition (one lagging) vs uniform lag; hypothesize cause each.
3. Plot lag over 30 min; compute growth rate msg/s (`Δlag/Δt`).
4. Correlate lag start with deploy/GC/rebalance log line.
5. Check consumer assignment: are partitions evenly owned?
6. Tune `max.poll.records` 500→50; measure rebalance frequency change.
7. Trigger a rebalance (rolling restart); time no-progress window.
8. Produce a poison pill (bad JSON); watch retry loop + lag climb.
9. Route poison pill to DLQ after 3 retries; verify lag recovers.
10. Measure end-to-end latency via `record.timestamp` vs consume time.
11. Build lag heatmap by partition in Grafana.
12. Alert: `sum(lag) > 10k for 10 min` — test firing.
13. Compare scaling consumers 3→6 with only 3 partitions (prove no gain).
14. Check broker: `kafka-topics.sh --describe` ISR + under-replicated.
15. Document `session.timeout.ms` vs `max.poll.interval.ms` interplay.

## Part B — Fix & Harden (16–30)
16. Add async processing with bounded worker pool; re-measure throughput.
17. Implement exponential-backoff retry + DLQ headers (topic, partition, offset, error).
18. Add Micrometer `kafka.consumer.lag` gauge + consume-rate counter.
19. Autoscale rule: scale on lag, cooldown 5 min, max = partition count.
20. Partition sizing exercise: 12 partitions for 4 consumers — justify.
21. Idempotent consumer (DB unique key) enabling safe replay.
22. Chaos: kill one consumer, observe rebalance + lag spike + recovery time.
23. Broker drill: throttle one broker disk, watch fetch latency.
24. Backpressure: pause partitions (`consumer.pause()`) on downstream 429.
25. Runbook timing: describe → logs → broker → scale-or-skip in <10 min.
26. Post-mortem one-pager for 40-min lag incident.
27. SLI: p99 produce-to-consume latency <30s; SLO burn alert.
28. Load test 2× produce; record max sustainable throughput.
29. Peer-review retry/DLQ config for infinite-loop risk.
30. Write consumer checklist: partitions, poll sizes, timeouts, DLQ, dashboard.

Stretch: Burrow-based lag evaluation (status OK/WARN/ERR) + PagerDuty integration.
