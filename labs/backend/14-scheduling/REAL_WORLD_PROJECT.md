# Real World Project: Scheduling

## Project
a nightly ETL job guarded by ShedLock and idempotency keys.

## Why it matters
In production, Scheduling is rarely a library detail — it is an architectural commitment. Teams choose it to safe recurring jobs across restarts.

## Architecture sketch
```
Client -> API Gateway -> Scheduling Service -> Datastore
                |               |
                +-> Observability (logs/metrics/traces)
```

## Implementation notes
- Prefer constructor injection and small, testable components.
- Keep the happy path pure; isolate side effects.
- Version the contract and document it (OpenAPI/schema).
- Add timeouts, retries with backoff, and a circuit breaker at the boundary.
- Emit RED metrics (rate, errors, duration) and structured logs.

## Failure modes to design for
- Downstream timeout or partial failure.
- Retry storms amplifying load.
- Hidden shared mutable state across threads.
- Consistency windows between writes and reads.

## Testing the real thing
- Unit-test the service with mocks.
- Slice-test the web layer.
- Integration-test with Testcontainers against a real dependency.
- Load-test the p99 path with a small k6 script.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.spring.io/spring-framework/reference/integration/scheduling.html
- https://cron.hjw.io/

## Deliverables
- [ ] Working service with one happy and one error path
- [ ] Documented API surface
- [ ] Metrics and a dashboard panel
- [ ] A short retro: what surprised you, what you'd change
