# Lab 08: Observability — Logs, Metrics, Traces — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. The difference between a counter, gauge, histogram, and summary in Prometheus?**
- A) They are interchangeable
- B) Counter is monotonic and rate()-able; gauge is instantaneous and can go up or down; histogram has configurable buckets and supports `histogram_quantile`; summary gives quantiles but cannot be aggregated across instances
- C) Gauge is monotonic
- D) Summary can be aggregated across instances

**Answer: B** — Summaries cannot be aggregated (each instance computes its own quantiles), which makes them wrong for a fleet. Use histograms with buckets you chose deliberately.

---

**Q2. Which Prometheus query gives a true per-second rate from a counter?**
- A) `rate(http_requests_total[5m])`
- B) `avg_over_time(http_requests_total[5m])`
- C) `increase(http_requests_total[5m]) / 300`
- D) `http_requests_total`

**Answer: A** — `rate()` handles counter resets and extrapolation. `increase()` is also correct and is `/300` away from `rate()`; option C is arithmetic-equivalent to A only after resetting, so A is the idiomatic form.

---

**Q3. Why is a p99 latency SLO usually expressed as a histogram quantile rather than from a summary?**
- A) Summaries are cheaper
- B) Histogram buckets can be aggregated across all instances, so the quantile reflects the whole fleet; a summary's quantile is per-instance and a fleet-wide percentile computed from those is mathematically invalid
- C) Summaries lose resolution
- D) Prometheus only supports histograms

**Answer: B** — Aggregating percentiles is not associative. Summaries give you fleet-blind numbers.

---

**Q4. `histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))` returns 4.0 s when your bucket boundaries are `[0.1, 0.25, 0.5, 1, 2.5, 5]`. What is wrong?**
- A) The query syntax
- B) The true p99 lies in the `2.5–5` bucket, so the interpolation is unusable for an SLO of 200 ms — buckets must straddle your SLO threshold
- C) `rate` must be `irate`
- D) You need `sum by (le, instance)`

**Answer: B** — Bucket design is a decision with numerical consequences. If your SLO is 200 ms, a bucket boundary must sit just below it, or you cannot measure the error rate for your SLO at all.

---

**Q5. Why is an SLI defined as "ratio of good events to valid events" rather than "average latency"?**
- A) Ratios are cheaper to compute
- B) A ratio is directly interpretable as a percentage of user-visible success, which makes an error budget meaningful and burn-rate alerts possible; averages hide the tail and the worst case
- C) Averages cannot be computed
- D) Ratios work without instrumentation

**Answer: B** — `good / valid` is what a user experiences. Latency thresholds are a different SLI family; you usually need both.

---

**Q6. With an SLO of 99.9% over 30 days, how much error budget remains after 30 minutes of complete outage?**
- A) 100% remains
- B) 30 days × 0.1% = 43.2 min of budget, so 13.2 min remain (about 31% of budget)
- C) 30 minutes remain
- D) The budget is exhausted

**Answer: B** — Error budget is expressed in allowed-failure *time*, which makes it directly spendable and comparable.

---

**Q7. A multi-window multi-burn-rate alert uses a 1-hour burn rate of 14.4× on an SLO with a 30-day window. What does that mean operationally?**
- A) The service will be fully down
- B) At this rate the entire 30-day budget is consumed in ~2 days, so burn the page; it is fast enough to catch a real outage but slow enough to avoid noise
- C) 14.4 errors per second
- D) The SLO will be missed by 14.4%

**Answer: B** — Page on fast burns (exhausting budget in days), ticket on slow burns (exhausting in weeks). The 14.4×/6× factors come from the standard 1%/10% budget-consumption-over-window rule.

---

**Q8. Why does a trace with sampling at 1% still find your bug?**
- A) Sampling increases volume
- B) Tail-based/priority sampling keeps every slow or errored request and drops a fraction of boring ones, so rare failures are retained at a fraction of the cost
- C) Traces are never sampled
- D) Because errors are deterministic

**Answer: B** — Head-based sampling is biased: it drops exactly the requests you need. Tail-based sampling decides *after* the trace completes.

---

**Q9. What does an OpenTelemetry span's `trace_id` buy you that a request ID does not?**
- A) Better compression
- B) A globally unique id that correlates the full call tree — parent/child causality across services, plus span timing and attributes, so you can see *which hop* consumed the time
- C) Automatic retries
- D) Sampling control

**Answer: B** — A request ID you generate yourself works, but a trace ID with structured spans and parent links turns a string into a call graph.

---

**Q10. Logs vs metrics vs traces: when do you reach for each?**
- A) Traces always, since they are richest
- B) Metrics for "is it bad and how bad" (cheap, aggregated, alertable), traces for "which specific thing is slow/failing" (high-cardinality, sampled), logs for arbitrary detail with correlation ids to tie them to both
- C) Logs for alerting, traces for dashboards
- D) Metrics for debugging single requests

**Answer: B** — The pillars are complementary, and the economics differ by orders of magnitude. Metrics are stored; traces are sampled; logs are searchable.

---

**Q11. Cardinality explosion happens when you...?**
- A) Add a `service` label
- B) Put unbounded or high-cardinality values in a metric label — user ID, request ID, full URL path, exception message, raw SQL
- C) Increase the scrape interval
- D) Add a recording rule

**Answer: B** — Each unique label combination is a separate time series in memory and on disk. A user ID label can create millions of series per metric and take down the Prometheus process itself.

---

**Q12. Why should a Java service propagate W3C `traceparent` rather than generate a new trace per inbound hop?**
- A) It is smaller
- B) The incoming context must be extracted and the outgoing span created as a child; starting a new trace per hop fragments the causal chain and makes end-to-end latency unmeasurable
- C) `traceparent` avoids sampling
- D) Required by OpenTelemetry spec for all outbound calls

**Answer: B** — Also note: `AsyncSpan` must be explicitly ended in async work (e.g. `CompletableFuture`), or you leak spans and never see the child complete.

---

**Q13. A dashboard shows p50 latency flat at 80 ms while users report timeouts. What is happening?**
- A) Users are wrong
- B) The tail degraded — p50 is blind to it. You need p95/p99/p99.9 and an error/timeout rate, plus concurrency, because tail latency usually appears first as a concurrency and saturation symptom
- C) The metrics are stale
- D) The service restarted

**Answer: B** — Averages hide exactly the class of problem users report. This is the single best argument for percentile SLIs.

---

**Q14. What is the practical purpose of an SLO-based *reduction* (burn-rate) alert rather than a threshold on a raw metric?**
- A) It is cheaper to evaluate
- B) It alerts on how fast you are consuming the *business* reliability promise, which is scale-free and directly tied to the decision (page vs ticket) instead of an arbitrary absolute threshold
- C) It uses fewer metrics
- D) It replaces SLOs

**Answer: B** — Raw thresholds produce both false positives during safe periods and false negatives during slow burns. Burn rate ties alerting to the promise.

---

**Q15. The single most common reason teams fail to reduce incident MTTR with observability investment is?**
- A) They did not buy enough storage
- B) They instrumented but never connected signals to *action* — no runbook link in the alert, no `service`/`env` label on the dashboard, no request-id correlation in the logs, so the data arrives after the incident is over
- C) They used too many metrics
- D) They did not use tracing

**Answer: B** — Observability without an operational path is a museum. Every alert needs a runbook, every dashboard needs a scope, every log line needs a correlatable id.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and instrument a real service.
- 12–10: revisit histogram/bucket design and SLO math; redo EXERCISES 2–5.
- <10: re-read THEORY cold, then build a trivial instrumented service end-to-end before retaking.
