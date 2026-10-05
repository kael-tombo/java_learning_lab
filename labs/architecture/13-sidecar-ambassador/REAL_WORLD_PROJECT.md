# Real-World Project — Sidecar and Ambassador Patterns

## Scenario

A global logistics company operates a microservices architecture with
hundreds of services across multiple regions. Each service needs
consistent cross-cutting behavior: mutual TLS authentication, request
retries, circuit breaking, rate limiting, distributed tracing, and
metrics collection. Implementing these in each service would be
error-prone and difficult to maintain. The company adopts the sidecar
pattern with a service mesh (Istio/Linkerd) to provide these concerns
transparently.

## System Overview

Each service pod contains two containers:

| Container | Responsibility |
|-----------|---------------|
| Application | Business logic only |
| Sidecar Proxy | Cross-cutting concerns |

The sidecar proxy (Envoy-based) handles:
- **mTLS**: mutual TLS authentication between services
- **Retries**: automatic retry with exponential backoff
- **Circuit breaking**: fail fast when services are unhealthy
- **Rate limiting**: protect services from overload
- **Tracing**: distributed tracing with OpenTelemetry
- **Metrics**: Prometheus metrics for all traffic
- **Traffic splitting**: canary deployments and A/B testing

## Architecture Decisions

### Sidecar Implementation
- **Envoy proxy** as the sidecar (used by Istio, Linkerd)
- **Transparent proxying**: iptables rules redirect traffic through sidecar
- **xDS protocol**: dynamic configuration from control plane
- **Hot restart**: sidecar updates without dropping connections

### Cross-Cutting Concerns
- **mTLS**: automatic certificate rotation, zero-trust security
- **Retries**: configurable per-route with backoff and timeout
- **Circuit breaking**: connection pool limits, outlier detection
- **Rate limiting**: global and per-service rate limits
- **Observability**: metrics, logs, and traces for all traffic

### Operational Benefits
- **Language agnostic**: sidecar works with any language
- **Consistent behavior**: all services get identical cross-cutting behavior
- **Independent updates**: sidecar updated without application changes
- **Centralized control**: control plane manages all sidecars

## Implementation Phases

### Phase 1: Foundation
1. Set up Kubernetes cluster
2. Deploy service mesh (Istio/Linkerd)
3. Configure sidecar injection
4. Enable mTLS between services

### Phase 2: Traffic Management
5. Configure retry policies
6. Set up circuit breakers
7. Implement rate limiting
8. Add traffic splitting for canary deployments

### Phase 3: Observability
9. Enable distributed tracing
10. Configure metrics collection
11. Set up access logging
12. Build observability dashboards

### Phase 4: Operations
13. Implement sidecar hot restart
14. Add sidecar resource limits
15. Configure sidecar health checks
16. Build sidecar update automation

## Sourced Field Notes (fetched Oct 2026 — verify before citing)

- **Istio Service Mesh**: https://istio.io/latest/docs/concepts/what-is-istio/
  Official Istio documentation explaining the service mesh architecture,
  sidecar pattern, and traffic management capabilities.

- **Linkerd Service Mesh**: https://linkerd.io/2.12/overview/
  Linkerd's overview of its lightweight service mesh, including
  sidecar proxy architecture and operational simplicity.

## Success Metrics

- mTLS coverage: 100% of service-to-service traffic
- Retry success rate: over 95% of transient failures recovered
- Circuit breaker activations: monitored and alerted
- Sidecar resource usage: under 10% of pod resources
- Zero application code changes for cross-cutting concerns

## Lessons from Production

1. **Start with mTLS and observability** — these provide immediate
   value and are the foundation for other features.

2. **Monitor sidecar resource usage** — sidecars consume CPU and memory;
   set resource limits and monitor to prevent resource exhaustion.

3. **Plan for sidecar updates** — sidecars will need updates (security
   patches, new features); ensure hot restart works and test updates.

4. **Don't ignore the learning curve** — service meshes add complexity;
   invest in training and documentation for operations teams.
