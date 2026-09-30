# CHECKLIST: Distributed Resilience Readiness
## Lab 04 | Production Engineering Academy

---

## 1. Network & Timeout Gates
- [ ] Connect timeout explicitly set on all HTTP/gRPC clients ($\le 500\text{ms}$).
- [ ] Read/socket timeout explicitly set on all outbound calls (capped at $\le 2,000\text{ms}$).
- [ ] Connection pool max size aligned with downstream concurrency capacity.
- [ ] Connection idle timeout and keepalive configured to prune stale socket connections.

## 2. Fault Isolation & Protection
- [ ] Circuit breaker configured for all remote external dependencies.
- [ ] Fallback method defined: returns graceful cached data, default value, or fast 503 instead of throwing unhandled exceptions.
- [ ] Bulkhead thread pools or semaphore limits isolate slow downstream calls from main request workers.
- [ ] Retries disabled on non-idempotent endpoints (POST payment, checkout).
- [ ] Retries configured with exponential backoff and randomized jitter on idempotent operations.

## 3. Graceful Degradation & Chaos Validation
- [ ] Tested behavior when downstream dependency latency increases to 10 seconds.
- [ ] Tested behavior when downstream dependency returns 100% 500 errors.
- [ ] Chaos mesh or Toxiproxy used to inject 20% packet loss in staging.
- [ ] Liveness and readiness probes run on separate management port to prevent health probe timeout under traffic saturation.
