# Lab 08: Observability — Logs, Metrics, Traces — Flashcards

~60 cards. Most answers are a query, a threshold, or a number.

---

## SLIs and SLOs

Q: What is an SLI?
A: A precisely defined measure of service behaviour from the user's perspective (e.g. "fraction of requests that returned non-5xx in < 200 ms").

Q: What is an SLO?
A: A target for an SLI over a stated window (e.g. 99.9% of requests over 28–30 days). A promise, not a hope.

Q: What is an error budget?
A: The allowed failure: `(1 − SLO) × window`. In minutes of outage for a time-window SLO, in requests for a volume-window one.

Q: 99.9% over 30 days → error budget?
A: `0.1% × 43,200 min = 43.2 min`.

Q: Why 28 days instead of 30?
A: Aligns with Google's SRE workbook practice; a 28-day window shifts smoothly with monthly reporting and avoids partial-month confusion.

Q: Request-based vs time-based SLI window?
A: Request-based (`good/valid` over N requests) is better for traffic-sparse services; time-based is better for continuously-available services.

Q: Should availability and latency be one SLI or two?
A: Two. Availability ("did it work") and latency ("was it fast enough") fail differently and alert differently.

Q: What is a "valid event" exclusion?
A: Requests that are not eligible to count (e.g. client-cancelled, filtered by a tenant allowlist, or below a minimum response time). Must be defined explicitly or the SLI is ambiguous.

Q: 99% / 99.9% / 99.99% in minutes per 30 days?
A: 432 / 43.2 / 4.3 minutes.

Q: Three nines in requests per day?
A: At 1M req/day, 0.1% = 1,000 failures/day allowed.

Q: Error budget as a *release* policy?
A: Policy: while budget > 50% remaining, ship freely; 25–50%, ship with extra canary scrutiny; <25%, freeze non-essential changes. Budget exhaustion is allowed to freeze releases.

Q: What is an SLI dashboard minimum?
A: SLI value, error budget remaining, burn rate (fast + slow), and request volume (denominator sanity).

---

## Metrics & Prometheus

Q: Counter, gauge, histogram, summary?
A: Counter (monotonic, `rate()` it), gauge (instantaneous), histogram (bucketed, aggregatable), summary (client-side quantiles, NOT aggregatable).

Q: Correct rate query for a counter?
A: `rate(metric[5m])`. Handles resets and extrapolation.

Q: Correct p99 from a histogram?
A: `histogram_quantile(0.99, sum by (le) (rate(metric_bucket[5m])))`.

Q: Why not use `avg_over_time` for counters?
A: Averages are meaningless for monotonic values and break across resets/rollouts.

Q: Rule of thumb for `rate()` window?
A: At least 4× the scrape interval so you get ≥4 samples; longer for stability. 5m for dashboards, 1–2m for alerts.

Q: Cardinality budget per metric?
A: Aim for hundreds, not millions. Count distinct `label` combinations with `count(count by (job,instance,all_labels)(metric))` style queries.

Q: Dangerous labels in Java metrics?
A: `userId`, `requestId`, `sessionId`, full URL with path params, raw exception message/stack, SQL text, arbitrary `Map` keys from tags.

Q: Rule of thumb for bucket count?
A: 10–20 buckets, chosen to straddle your SLO threshold. Too few → unusable interpolation; too many → cost/cardinality.

Q: Buckets for an SLO of 200 ms?
A: Something like `.05 .1 .15 .2 .25 .3 .5 .75 1 2 3 5 10` — boundary exactly at 0.2 so `le="0.2"` is the SLO numerator.

Q: `le` label semantics?
A: "less than or equal" — cumulative. `le="0.2"` counts requests ≤ 200 ms. Buckets must include `+Inf`.

Q: Micrometer config for percentiles?
A: `management.metrics.distribution.percentiles-histogram.http.server.requests: true` plus `percentiles` for client-side quantiles (cheaper, but you lose server-side aggregation of the client side).

Q: `management.metrics.tags.application` used for?
A: Adding a common low-cardinality tag (app, env, version) to every metric so multi-service dashboards work.

Q: Recording rule?
A: Precompute expensive aggregations so dashboards and alerts run cheap queries. Always label with the full label set you group by.

Q: Exemplars?
A: Link a histogram bucket observation to a trace ID — jump from "latency is bad in this bucket" to the exact slow trace.

Q: `@Timed` vs `Observation` in Spring Boot 3?
A: `Observation` produces both a metric and a span with the same name, giving metrics/traces correlation for free. Prefer it over `@Timed` for new code.

Q: Cardinality guard in Micrometer?
A: `MeterFilter.maximumAllowableTags(...)` to cap dynamic tag values and fail fast in dev.

Q: JVM metrics worth alerting on?
A: GC pause time rate, old-gen occupancy growth rate, `heap_used/heap_max`, thread count, `process_cpu_time` vs wall time.

Q: Micrometer/actuator endpoint?
A: `/actuator/prometheus` (requires `micrometer-registry-prometheus`).

---

## Logging

Q: Structured logging format for machines?
A: JSON (logstash encoder / ECS / OpenTelemetry log format) — key/value parsing beats regex on a human line.

Q: Correlation id to put in every log line?
A: `trace_id` (and `span_id`), plus a `request_id` if you have an ingress-generated one. This is what makes logs joinable to traces.

Q: Pattern vs structured layout?
A: Pattern is fast to write, brittle to parse. Structured costs a little CPU and is the only sane choice at fleet scale.

Q: Log levels in production for a request path?
A: `INFO` sparingly (business-significant, sampled), `WARN` for degradation, `ERROR` for actionable failure. `DEBUG` off by default. Do not log PII or tokens at any level.

Q: Async log appenders?
A: Async appenders keep logging off the request path (Logback `AsyncAppender`, Log4j2 `AsyncLogger` with `ringBufferSize`). Trade: you lose the last few lines on crash — which is exactly when you want them, so also log the crash to stderr synchronously.

Q: Logs-as-metrics bridge?
A: Count log lines by severity/exception class (`logback_metrics` or a log pipeline) so "error log rate" can be an SLI and alert. Also logfmt-friendly.

Q: Retention for logs?
A: Hot 7–14 days in fast storage, warm 30–90 days compressed, cold 1–2 years for audit. Cost scales with volume, so sample high-volume INFO.

Q: Sampling high-volume success logs?
A: Sample at 1% for 200s on high-QPS paths, keep 100% for errors and slow requests.

Q: MDC / structured context in Java?
A: `MDC.put("request_id", id)` in a filter; cleared in a `finally`. Thread pools need `TaskDecorator` or `InheritableThreadLocal` plus explicit clear, else ids leak between requests.

Q: MDC leak symptom?
A: Wrong correlation ids on some requests only — almost always an un-cleared MDC on a pooled thread.

---

## Tracing & OpenTelemetry

Q: Three pillars?
A: Metrics, logs, traces. Each answers a different question; none substitutes for another.

Q: Span vs trace?
A: A trace is the whole request across services (one `trace_id`); a span is one operation within it (one `span_id`, with `parent_span_id`).

Q: W3C context propagation?
A: `traceparent` and `tracestate` headers. Extract inbound, inject outbound, create child spans.

Q: Java agent approach?
A: `java -javaagent:opentelemetry-javaagent.jar -Dotel.service.name=...` — auto-instruments Spring MVC, JDBC, HTTP clients, Kafka.

Q: Manual approach?
A: `GlobalOpenTelemetry.getTracer(...)`, explicit `Tracer.spanBuilder(...)`. Use when you need custom attributes or to instrument things the agent misses.

Q: SDK wiring for Spring Boot 3?
A: `micrometer-tracing-bridge-otel` + `opentelemetry-exporter-otlp` + `opentelemetry-sdk-extension-autoconfigure`. Sends spans to OTLP (Collector → Tempo/Jaeger).

Q: Head-based vs tail-based sampling?
A: Head-based decides at span start (biased: drops the interesting slow/error spans); tail-based decides at trace end (keeps all errors + slow traces, samples the rest). Head-based cannot see the outcome.

Q: Recommended default sampling for a Java service?
A: Parent-based (respect upstream decision) + probability for the root, plus always record errors/exceptions. Tail-based requires a Collector.

Q: Span attributes worth recording on a server span?
A: `http.method`, `http.route` (templated path, never the raw URL), `http.status_code`, `db.system`, `db.statement` (templated), `messaging.destination`, `retries`, `user.tier` (low cardinality).

Q: Span events?
A: Timestamps within a span — e.g. "retry attempted", "circuit breaker opened", "cache miss". Cheaper than more spans and often more useful.

Q: Where must you explicitly end a span in Java async code?
A: `CompletableFuture` / `Executor` tasks — the parent scope does not auto-propagate. Use `AsyncSpan.end()` in a `whenComplete`, or the Micrometer context-propagating executor.

Q: Trace sampling and cost control: what to do first?
A: Drop noisy internal spans (e.g. per-row loop spans), keep span attributes instead; then reduce root sampling rate; then move to a Collector tail-based policy.

Q: `traceparent` must be forwarded across a queue?
A: Yes — inject into message headers so the consumer continues the trace; otherwise async flows become orphan traces with no end-to-end latency.

Q: What does an "orphan" span tell you?
A: A trace with a `span_id` but no parent in your system — usually a lost context-propagation point, which is a real bug in your instrumentation.

---

## Alerting & SRE

Q: Symptom-based vs cause-based alerting?
A: Symptom = user-visible (error rate, latency); cause = internal resource. Alert on symptoms; use causes for diagnosis and dashboards. Cause-based paging generates noise.

Q: Burn rate definition?
A: `observed_bad_rate / allowed_bad_rate`. `>1` means the budget is being consumed faster than sustainable.

Q: Burn rate to exhaust a 30-day budget in 1 day?
A: `30×`. In 3 days: `10×`. In 30 days: `1×`.

Q: Recommended multi-window multi-burn-rate config?
A: Page: burn `14.4×` over 1h **and** `5×` over 6h (≈2-day and ≈6-day exhaustion). Ticket: `1×` over 6h **and** `1×` over 3d. The AND across windows kills flapping.

Q: Alert fatigue metric?
A: Pages per on-call shift that do not require action. Target < 1–2 per shift; track it.

Q: Every page must have?
A: A runbook link, an owner, a `severity` label, and an unambiguous "what good looks like" (expected value vs threshold).

Q: Detection time vs resolution time?
A: `MTTD` = detection (alerting design), `MTTR` = resolution (runbooks, access, automation). Observability mainly moves MTTD; runbooks move MTTR.

Q: Golden signals?
A: Latency, traffic, errors, saturation. Start any dashboard there, then add domain SLIs.

Q: What is an "error budget policy" for a team?
A: A written rule connecting remaining budget to acceptable release risk. Without it, the budget is just a number nobody acts on.

Q: SLO review cadence?
A: Monthly: error budget burn, SLI trend, alert quality (false positives), and whether the SLI still reflects what users care about.

Q: What makes an SLO *bad*?
A: One that measures the wrong thing (queue depth instead of user latency), is trivially satisfiable (errors on empty traffic), or has no policy attached.

---

## Numbers to memorize

Q: Error budget for 99.9% / 30 days?
A: 43.2 minutes.

Q: Error budget for 99.95% / 30 days?
A: 21.6 minutes.

Q: Error budget for 99.99% / 30 days?
A: 4.3 minutes.

Q: Burn rate to exhaust 30-day budget in 1 day / 3 days / 30 days?
A: 30× / 10× / 1×.

Q: Standard page-burn threshold pair?
A: 14.4× (1h) and 5× (6h).

Q: PromQL p99 idiom?
A: `histogram_quantile(0.99, sum by (le) (rate(metric_bucket[5m])))`.

Q: Default `rate()` window rule?
A: ≥ 4× scrape interval.

Q: Bucket count for a latency histogram?
A: 10–20, with a boundary at your SLO threshold.

Q: Days in 30?
A: 43,200 minutes. Budget in minutes = `0.001 × 43,200`.

Q: Target pages per on-call shift?
A: ≤ 1–2 actionable.
