# Mini Project — Sidecar and Ambassador Patterns

## Goal

Build a microservices system where each service has a sidecar proxy
that handles logging, retries, and circuit breaking. Demonstrate how
the sidecar transparently intercepts and enhances network calls
without changing the main application code.

## Requirements

### Main Services

1. **Order Service** — processes orders
2. **Payment Service** — processes payments
3. **Inventory Service** — manages stock

### Sidecar Proxy (Ambassador)

Each service has a sidecar that proxies all outbound HTTP calls:

**Responsibilities:**
- **Logging** — log all outbound requests and responses
- **Retries** — retry failed requests with exponential backoff
- **Circuit breaker** — stop calling failing services
- **Metrics** — collect request count, latency, error rate

### Demonstration

1. Order Service calls Payment Service through sidecar
2. Sidecar logs the request
3. If Payment Service fails, sidecar retries
4. If Payment Service keeps failing, circuit breaker opens
5. Order Service gets immediate error (no timeout wait)

## Technical Specifications

1. **Sidecar deployment**
   - Sidecar runs as a separate process in the same container/pod
   - Main service calls localhost:sidecar-port instead of direct service URL
   - Sidecar forwards calls to actual service URLs

2. **Logging**
   - Log all requests: timestamp, method, URL, status, duration
   - Log all responses: status, body size, duration
   - Structured logging (JSON format)

3. **Retries**
   - Retry on connection errors and 5xx responses
   - Exponential backoff: 100ms, 200ms, 400ms
   - Max 3 retries per request

4. **Circuit breaker**
   - Open circuit after 5 consecutive failures
   - Half-open after 30 seconds (test with one request)
   - Close circuit if test request succeeds

## Steps

1. Implement Order, Payment, and Inventory services
2. Build sidecar proxy with logging
3. Add retry logic to sidecar
4. Add circuit breaker to sidecar
5. Add metrics collection to sidecar
6. Deploy services with sidecars
7. Test happy path (all services up)
8. Test retry behavior (service temporarily down)
9. Test circuit breaker (service permanently down)
10. Verify main services have no sidecar-related code

## Acceptance Criteria

- [ ] Sidecar logs all outbound requests and responses
- [ ] Sidecar retries failed requests with backoff
- [ ] Circuit breaker opens after consecutive failures
- [ ] Circuit breaker closes after successful test request
- [ ] Main services have zero sidecar-related code
- [ ] Sidecar can be updated without changing main services
- [ ] Metrics are collected for all proxied calls

## Stretch Goals

- Implement sidecar for inbound calls (ambassador pattern)
- Add request/response transformation in sidecar
- Implement distributed tracing across sidecars
- Add configuration hot-reloading in sidecar
