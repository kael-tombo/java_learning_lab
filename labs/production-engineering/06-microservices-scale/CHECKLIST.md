# CHECKLIST: Microservices Production Readiness at Scale
## Lab 06 | Production Engineering Academy

---

## 1. Network & Protocol Standards
- [ ] JVM DNS TTL configured (`networkaddress.cache.ttl=10`).
- [ ] gRPC channels configured with client-side load balancing (`round_robin`).
- [ ] gRPC servers configure `maxConnectionAge` (e.g. 5m) to force periodic connection rebalancing.
- [ ] gRPC keepalive pings configured to detect dead connections across NAT gateways.
- [ ] Maximum message size explicitly configured on both client and server stubs.

## 2. Service Discovery & Topology
- [ ] Kubernetes readiness probes verify service can accept traffic before joining endpoints.
- [ ] Envoy/Istio sidecar memory and CPU requests/limits properly sized.
- [ ] Circuit breaker and rate limits applied at service egress.

## 3. Observability & Tracing
- [ ] OpenTelemetry W3C tracecontext headers (`traceparent`, `tracestate`) propagated across all HTTP and gRPC boundaries.
- [ ] Latency percentiles (p50, p95, p99, p99.9) tracked per RPC method.
