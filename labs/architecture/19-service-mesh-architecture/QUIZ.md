# Service Mesh Architecture Quiz

## Questions

1. **Data Plane vs Control Plane**: Explain the separation. What runs in the data plane (sidecar)? What runs in the control plane? Why is this separation critical for security and scalability?

2. **Sidecar Proxy Responsibilities**: List 5 responsibilities of the sidecar proxy (Envoy). Which are L4 vs L7? Which require service registry integration?

3. **mTLS Implementation**: How does a service mesh implement mutual TLS? Describe the certificate lifecycle: issuance, rotation, revocation. What is SPIFFE/SPIRE?

4. **Traffic Splitting**: You want to canary deploy v2 of a service (10% traffic). Show the VirtualService/DestinationRule (Istio) or HTTPRoute (Gateway API) config. How does the mesh ensure session affinity if needed?

5. **Retry + Timeout + Circuit Breaker**: In Istio, you configure `retries: 3, perTryTimeout: 2s, timeout: 10s`. A request fails 3 times with 1.5s each. Total time? What if the 3rd retry takes 3s? How does circuit breaker (outlier detection) interact?

6. **Authorization Policies**: Difference between `PeerAuthentication` (mTLS), `AuthorizationPolicy` (RBAC), and `RequestAuthentication` (JWT). When to use each? Show a policy allowing only `payment-service` to call `billing-service` on `/charge`.

7. **Observability - Distributed Tracing**: How does the mesh inject trace context? What headers (W3C trace-context, B3)? If application doesn't propagate headers, what breaks? How to fix?

8. **Multi-Cluster / Multi-Network**: Two clusters in different VPCs. How does service mesh handle cross-cluster service discovery? What is `ServiceEntry` / `ClusterEntry`? Describe the control plane replication model.

9. **Performance Overhead**: Sidecar adds ~2-5ms latency per hop. For a 10-hop request chain, that's 20-50ms. What optimizations exist? (e.g., protocol upgrade, ztunnel, ambient mesh). When would you NOT use a service mesh?

10. **Incident**: All sidecars in namespace `prod` show `503` for external egress. Control plane is healthy. Debugging steps: check `Envoy` config dump, `istioctl proxy-config`, egress gateway, `ServiceEntry` for external domains.

---

## Answers

1. **Data Plane**: Sidecar proxies (Envoy) in each pod — handle actual traffic (L4/L7 proxy, mTLS, retries, metrics). **Control Plane**: Istiod/Linkerd controller — config distribution, certificate management, service discovery, policy enforcement. **Separation**: Data plane scales with workloads; control plane scales with config complexity. Security: compromise of one sidecar doesn't expose control plane.

2. **Sidecar Responsibilities**:
   - L4: TCP proxy, mTLS termination, load balancing (round-robin, least request)
   - L7: HTTP routing, retries, timeouts, fault injection, rate limiting, authz
   - Observability: metrics (Prometheus), traces (headers), access logs
   - Service registry: SDS (Secret Discovery Service), EDS (Endpoint Discovery Service)

3. **mTLS Flow**:
   - Control plane (Istiod) acts as CA or integrates with SPIRE
   - Workload identity: `spiffe://cluster.local/ns/default/sa/payment-service`
   - Certs issued via SDS API, rotated every 24h (default), 1h before expiry
   - Revocation: CRL or short-lived certs (no revocation needed)
   - **SPIFFE**: Standard for workload identity. **SPIRE**: Implementation (agent + server).

4. **Canary Config (Istio)**:
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
spec:
  hosts: ["billing-service"]
  http:
  - route:
    - destination: { host: billing-service, subset: v1 }
      weight: 90
    - destination: { host: billing-service, subset: v2 }
      weight: 10
---
kind: DestinationRule
spec:
  host: billing-service
  subsets:
  - name: v1
    labels: { version: v1 }
  - name: v2
    labels: { version: v2 }
```
Session affinity: `consistentHash` on header/cookie in `DestinationRule`.

5. **Timing**: 
   - 3 retries × 1.5s = 4.5s < 10s timeout → succeeds on 3rd retry
   - If 3rd retry 3s: 1.5+1.5+3 = 6s < 10s → succeeds
   - If total > 10s: timeout triggers, request fails
   - **Outlier detection** (circuit breaker): Tracks 5xx per endpoint. If > threshold, ejects host from LB pool. Independent of retry policy.

6. **Policy Types**:
   - `PeerAuthentication`: mTLS mode (STRICT, PERMISSIVE)
   - `RequestAuthentication`: JWT validation (issuer, audiences)
   - `AuthorizationPolicy`: RBAC (allow/deny rules on source, path, method)
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata: { name: billing-auth, namespace: prod }
spec:
  selector: { matchLabels: { app: billing-service } }
  rules:
  - from:
    - source: { principals: ["cluster.local/ns/prod/sa/payment-service"] }
    to:
    - operation: { paths: ["/charge"], methods: ["POST"] }
```

7. **Trace Context**: Sidecar injects `traceparent`, `tracestate` (W3C) or `x-b3-*` (B3) on ingress. **App must propagate** headers on outbound calls. If not: trace breaks at that service. Fix: auto-instrumentation (OpenTelemetry Java agent) or middleware.

8. **Multi-Cluster**:
   - **Primary-Remote**: Single control plane (primary) manages remote clusters via secrets
   - **Multi-Primary**: Each cluster has control plane, share config via federation
   - Cross-cluster discovery: `ServiceEntry` with `endpoints` from remote cluster
   - `ClusterEntry` (Gateway API): Standardized multi-cluster service import

9. **Optimizations**:
   - **Ambient Mesh** (Istio): ztunnel (L4) per node + waypoint (L7) per namespace — no sidecar per pod
   - **Protocol upgrade**: h2c, HTTP/3
   - **Connection pooling**: Reuse upstream connections
   - **Don't use mesh**: Simple apps (< 10 services), high-perf requirements (sub-ms), team lacks ops capacity

10. **Debugging Egress 503**:
    1. `istioctl proxy-config listener <pod> -n prod` — check egress listeners
    2. `istioctl proxy-config route <pod> -n prod` — check virtual outbound routes
    3. Verify `ServiceEntry` for external domain exists
    4. Check egress gateway logs (if used)
    5. `istioctl x authz check <pod>` — verify authz policies
    6. Capture Envoy config dump: `istioctl proxy-config all <pod> -o json`