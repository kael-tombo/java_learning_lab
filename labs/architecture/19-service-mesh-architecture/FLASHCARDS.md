# Service Mesh Architecture Flashcards

## Fundamentals

**Q: What is a service mesh?**
**A:** Dedicated infrastructure layer for service-to-service communication. Provides traffic management, security, observability via sidecar proxies.

**Q: Data plane vs Control plane?**
**A:** Data plane = sidecar proxies (Envoy) handling traffic. Control plane = config distribution, cert management, service discovery (Istiod).

**Q: Why sidecar pattern?**
**A:** Transparent to application. No code changes. Language-agnostic. Uniform policy enforcement.

**Q: What is Envoy?**
**A:** High-performance L4/L7 proxy. Core of Istio, Linkerd, Consul Connect, AWS App Mesh.

---

## Traffic Management

**Q: VirtualService vs DestinationRule (Istio)?**
**A:** VirtualService = routing rules (match, rewrite, split). DestinationRule = LB policy, subsets, circuit breaker, TLS.

**Q: Traffic splitting for canary?**
**A:** VirtualService with weighted routes to subsets (v1: 90%, v2: 10%).

**Q: Retry policy config?**
**A:** `retries`, `perTryTimeout`, `retryOn` (connect-failure, refused-stream, 5xx, retriable-4xx).

**Q: Timeout vs Retry interaction?**
**A:** Total time = sum of perTryTimeout × attempts. Bounded by global `timeout`.

**Q: Fault injection?**
**A:** Inject delays/aborts for chaos testing. `delay: { percentage, fixedDelay }`, `abort: { percentage, httpStatus }`.

**Q: Circuit breaker (outlier detection)?**
**A:** Tracks 5xx per host. Consecutive 5xx → ejection. Config: `consecutive5xxErrors`, `interval`, `baseEjectionTime`.

**Q: Mirroring / Shadow traffic?**
**A:** Copy production traffic to new version (no response to client). For validation.

---

## Security (mTLS, AuthZ)

**Q: mTLS in service mesh?**
**A:** Automatic certificate issuance/rotation via SDS. Sidecar terminates mTLS. App sees plain HTTP.

**Q: SPIFFE / SPIRE?**
**A:** SPIFFE = standard for workload identity (`spiffe://trust-domain/ns/sa`). SPIRE = implementation (agent + server).

**Q: PeerAuthentication?**
**A:** Mesh-wide or namespace mTLS mode: STRICT (only mTLS), PERMISSIVE (accept both), DISABLE.

**Q: RequestAuthentication?**
**A:** JWT validation at ingress. Config: issuer, JWKS URI, audiences.

**Q: AuthorizationPolicy?**
**A:** L7 RBAC. Match: source (principal, namespace, IP), request (path, method, headers). Action: ALLOW/DENY.

**Q: Egress control?**
**A:** ServiceEntry for external domains. Egress gateway for centralized outbound. AuthorizationPolicy on egress.

---

## Observability

**Q: Distributed tracing headers?**
**A:** W3C: `traceparent`, `tracestate`. B3: `x-b3-traceid`, `x-b3-spanid`, `x-b3-sampled`.

**Q: Trace context propagation?**
**A:** Sidecar injects on ingress. **Application must propagate** on outbound. Auto-instrumentation (OTel) solves this.

**Q: Metrics from mesh?**
**A:** `istio_requests_total`, `istio_request_duration_seconds`, `istio_tcp_*`. Labels: source, destination, response_code.

**Q: Access logs?**
**A:** Envoy JSON logs. Custom format via `Telemetry` API. Ship to Loki/Elastic.

---

## Multi-Cluster / Advanced

**Q: Multi-cluster models?**
**A:** Primary-Remote (single control plane), Multi-Primary (federated control planes).

**Q: Cross-cluster service discovery?**
**A:** ServiceEntry with remote endpoints. Or Gateway API `ClusterEntry` / `ServiceImport`.

**Q: Ambient Mesh (Istio)?**
**A:** No sidecar per pod. ztunnel (L4, per node) + Waypoint (L7, per namespace). Lower overhead.

**Q: Gateway API vs Ingress?**
**A:** Gateway API: `GatewayClass`, `Gateway`, `HTTPRoute`, `TCPRoute`. Portable, expressive. Replaces Ingress.

---

## Operations

**Q: Debugging sidecar config?**
**A:** `istioctl proxy-config listener/route/cluster/endpoint <pod>`

**Q: Certificate rotation?**
**A:** Automatic via SDS. Default 24h TTL, rotated at 1h before expiry.

**Q: Upgrading mesh?**
**A:** Canary control plane upgrade. Data plane auto-upgrades via sidecar injector.

**Q: When NOT to use service mesh?**
**A:** < 10 services, extreme latency sensitivity, no ops team, simple north-south only.