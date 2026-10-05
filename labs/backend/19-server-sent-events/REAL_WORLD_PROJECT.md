# Real World Project: Server-Sent Events

## Project
a live metrics dashboard streaming SSE from Spring WebFlux.

## Why it matters
In production, Server-Sent Events is rarely a library detail — it is an architectural commitment. Teams choose it to live dashboards without WebSockets.

## Architecture sketch
```
Client -> API Gateway -> Server-Sent Events Service -> Datastore
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
- https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
- https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-async.html

## Deliverables
- [ ] Working service with one happy and one error path
- [ ] Documented API surface
- [ ] Metrics and a dashboard panel
- [ ] A short retro: what surprised you, what you'd change
