# Mini Project — Circuit Breaker Pattern

## Goal

Build a service that calls an external payment gateway with a circuit
breaker. Demonstrate the three states (closed, open, half-open) and
show how the circuit breaker prevents cascading failures.

## Requirements

### External Service (Simulated)

**Payment Gateway:**
- Simulated external service with configurable failure rate
- Can be healthy, degraded (slow), or down (failing)
- Endpoint: `POST /charge` — processes payment

### Circuit Breaker

**States:**
1. **Closed** — normal operation, requests pass through
2. **Open** — requests fail immediately, no calls to payment gateway
3. **Half-Open** — limited test requests to check recovery

**Configuration:**
- Failure threshold: 5 consecutive failures
- Timeout: 60 seconds (before half-open)
- Half-open max attempts: 1
- Success threshold (half-open): 1 success closes circuit

### Fallback

- When circuit is open, return cached response or default error
- Log circuit breaker state changes
- Notify monitoring system

## Technical Specifications

1. **State machine**
   - Implement circuit breaker as a state machine
   - Track consecutive failures and successes
   - Persist state for monitoring

2. **Failure detection**
   - Count consecutive failures
   - Open circuit when threshold reached
   - Reset counter on success

3. **Recovery testing**
   - After timeout, transition to half-open
   - Allow limited test requests
   - Close circuit on success, reopen on failure

4. **Monitoring**
   - Expose circuit breaker state via metrics
   - Log all state transitions
   - Alert on circuit open events

## Steps

1. Implement simulated payment gateway
2. Build circuit breaker state machine
3. Implement closed state (normal operation)
4. Implement open state (fail fast)
5. Implement half-open state (test recovery)
6. Add fallback logic
7. Add metrics and logging
8. Test with healthy service
9. Test with failing service (circuit opens)
10. Test recovery (circuit closes)

## Acceptance Criteria

- [ ] Circuit is closed during normal operation
- [ ] Circuit opens after 5 consecutive failures
- [ ] Requests fail fast when circuit is open
- [ ] Circuit half-opens after 60 seconds
- [ ] Circuit closes on successful test request
- [ ] Circuit reopens on failed test request
- [ ] Fallback response is returned when circuit is open
- [ ] State transitions are logged

## Stretch Goals

- Implement circuit breaker with sliding window (time-based)
- Add circuit breaker for multiple services
- Implement bulkhead pattern alongside circuit breaker
- Add circuit breaker dashboard for monitoring
