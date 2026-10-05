# VISION — Logging (SLF4J, Logback, Structured)

## Vision Statement
**Logs are data for strangers at 3 a.m.** — one event per line, correlation
IDs on every line, levels with meaning, so grep becomes querying and
incidents become joins instead of archaeology.

---

## Mental Models
### 1. Facade + Binding
Code to `SLF4J`, bind `Logback/Log4j2` once. Parameterized `{}` logging (no
`+` concat); guard expensive args; never log PII/secrets/tokens.
### 2. Levels Are Contracts
`ERROR` = page, `WARN` = degrade, `INFO` = business milestones, `DEBUG` =
diagnostics (off in prod), `TRACE` = wire detail. If ERROR doesn't page,
levels are lies.
### 3. Context Travels in MDC
`traceId/spanId/userId` in `MDC` propagate across threads (and clean up!).
Without correlation IDs, microservice logs are confetti.
### 4. Structure Beats Strings
JSON layout (`timestamp,level,logger,traceId,msg,kv`) ships to ELK/Loki;
plain `%msg` is for local dev only. Async appenders bound queue + drop policy.

---

## Decision Framework
| Question | Rule |
|----------|------|
| What to log? | Business outcomes + decisions, not every branch |
| Which level? | Would I page on it? ERROR : would I graph it? INFO |
| Add context? | MDC traceId always; clear in finally/filter |
| JSON or text? | JSON in prod, pretty in dev |
| Volume explodes? | Sample DEBUG, async+cap, alert on ERROR rate |

---

## Career Trajectory
- **L1:** SLF4J levels, parameterized logging, Logback config.
- **L2:** MDC propagation, JSON layout, rolling/file policies.
- **L3:** Pipeline design (shipper, index, retention), SLO on log error rate.
- **L4:** Observability strategy (logs × metrics × traces unification).

---

## 4-Week Path
```
W1: SLF4J/Logback, levels, parameterized + guard patterns.
W2: MDC + filters, virtual-thread propagation, JSON encoder.
W3: File policies, async appenders, ELK/Loki shipping lab.
W4: Checkout-service logging overhaul + error-budget dashboard.
```
## Success Metrics
- [ ] Every request traceable by traceId across 2 services
- [ ] ERROR rate alertable; zero secrets in 10k-line sample
- [ ] Async queue bounded; hot-loop logging cost measured
