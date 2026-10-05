# MINI PROJECT — Logging: Traceable Checkout Pipeline

## Goal (2 weeks, ~8–10h)
Overhaul a `System.out`-riddled checkout service into JSON-structured,
trace-correlated logging with an ERROR-rate SLO and a Loki/ELK-ready shipper.

## Requirements
### Functional
1. Replace all `println/printStackTrace` with SLF4J `{}` logging; guard
   expensive `toString`/`toJson` debug calls.
2. MDC: `traceId` (generated at edge, `X-Request-Id` honored), `userId`,
   `orderId` via servlet filter + `MDC.clear()` guarantee; propagate to
   `@Async`/virtual threads (wrapper or task decorator) — tested.
3. JSON layout in prod profile (`logstash-logback-encoder`): fields
   `ts,level,logger,traceId,userId,msg,stack_hash`; text pattern in dev.
4. Policies: size+time rolling (`50MB/7d`), async appender (queue 1024,
   `NEVER_BLOCK` + drop-count metric), `ERROR` file + console split.
5. Redaction: `PatternLayout`/`JsonGeneratorDecorator` masking
   `password|token|card|ssn`; unit test asserts masked output sample.
6. Dashboard: log-shipper (Filebeat/OTLP) to local Loki/Elasticsearch +
   Grafana panel: ERROR rate, p99 latency from access log, top exception.

### Non-functional
- 15+ tests: MDC propagation, redaction vectors, level contract (ERROR
  only on page-worthy), JSON schema validity, async-drop counter.
- Benchmark: logging overhead at 10k req (sync vs async) in README.
- README: level guide + traceId grep recipes + retention policy.

## Phases
### Week 1 — Code + Context (4–5h)
- Steps: SLF4J swap, filter+MDC, propagation wrapper, redaction.
- Deliverable: `traceId` end-to-end in local run.

### Week 2 — Ship + SLO (4–5h)
- Steps: JSON layout, rolling/async, shipper + dashboard, overhead bench.
- Deliverable: Grafana screenshot + SLO alert rule.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–15) | Fail (<12) |
|-----------|----------------|--------------|------------|
| SLF4J use | Parameterized + guarded | Mostly | Concat in hot path |
| MDC trace | Edge-to-async, cleared | Present | Missing/leaked |
| Structure | Valid JSON, queryable | JSON-ish | Plain strings |
| Redaction | Vectors masked + tested | Attempted | Secrets logged |
| Pipeline | Shipper + ERROR SLO panel | Files rotate | Console only |

Pass >= 70. Stretch: JFR `jdk.Logger` config audit; trace-logs exemplars;
log-based alert (`ERROR rate > 1%/5m`) with runbook link.
