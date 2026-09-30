# CHECKLIST: Observability & SRE Production Readiness
## Lab 08 | Production Engineering Academy

---

## 1. Metric Hygiene & Cardinality
- [ ] No high-cardinality tags (userId, UUIDs, orderId, email, timestamps) in Micrometer/Prometheus metrics.
- [ ] Explicit SLO latency histogram buckets defined for target endpoints.
- [ ] JVM GC and memory pool metrics exposed (`jvm.gc.pause`, `jvm.memory.used`).
- [ ] Metric scrape duration takes $< 500\text{ms}$ and payload size $< 2\text{MB}$.

## 2. Distributed Tracing & Context Propagation
- [ ] W3C `traceparent` header propagated across all outbound REST/gRPC/Kafka calls.
- [ ] OpenTelemetry span context mirrored to SLF4J MDC (`trace_id`, `span_id`).
- [ ] Trace context preserved across asynchronous thread hops (`CompletableFuture`, Virtual Threads).
- [ ] Head-based or tail-based trace sampling configured (e.g. 5% regular requests, 100% of errors and slow requests $> 500\text{ms}$).

## 3. Alerting & SLO Gates
- [ ] Multi-window, multi-burn-rate alerts configured for critical user journeys.
- [ ] PagerDuty / Opsgenie routing tested and verified.
- [ ] Runbooks linked directly inside alert notification payloads.
