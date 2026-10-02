# Service Mesh Deep Dive - Quiz

Test your understanding of Istio, Envoy, mTLS, traffic management, and observability.

---

## Questions

### 1. What are the two main components of Istio's architecture?
A) Control plane (Istiod) and data plane (Envoy sidecars)
B) API server and kubelet
C) Ingress gateway and egress gateway
D) Pilot and Citadel only

### 2. How does Istio achieve automatic sidecar injection?
A) MutatingAdmissionWebhook that adds Envoy container to pods with `sidecar.istio.io/inject: "true"` label/annotation
B) DaemonSet that runs Envoy on each node
C) Init container that rewrites iptables rules
D) CNI plugin that intercepts pod creation

### 3. What is mTLS in Istio and how does it work?
A) Mutual TLS where both client and server verify each other's certificates; Istio uses SDS (Secret Discovery Service) to distribute certs to Envoy
B) One-way TLS where only server presents certificate
C) TLS termination at ingress gateway only
D) Application-level encryption managed by developer code

### 4. Which Istio resource configures traffic splitting for canary deployments?
A) DestinationRule
B) VirtualService
C) ServiceEntry
D) Gateway

### 5. What is the difference between a VirtualService and a DestinationRule?
A) VirtualService defines routing rules (match/route); DestinationRule defines policies for traffic to a service (load balancing, circuit breaker, TLS)
B) VirtualService is for ingress; DestinationRule is for egress
C) They are the same thing with different names
D) VirtualService configures Envoy; DestinationRule configures Istiod

### 6. How does Istio's circuit breaker pattern work?
A) DestinationRule `trafficPolicy.connectionPool` and `outlierDetection` settings - Envoy tracks failures and ejects unhealthy endpoints
B) VirtualService `retries` and `timeouts` - retries failed requests
C) PeerAuthentication `STRICT` mode - blocks non-mTLS traffic
D) AuthorizationPolicy `DENY` - blocks traffic to failing services

### 7. What is the purpose of the Istio Ingress Gateway?
A) Manages external access to the mesh (load balancing, TLS termination, routing)
B) Encrypts service-to-service communication
C) Provides service discovery for external services
D) Monitors application metrics

### 8. Which telemetry components does Istio integrate with by default?
A) Prometheus (metrics), Jaeger/Zipkin (tracing), Fluentd/Logstash (logs) - via Envoy stats, OpenTelemetry, and access logging
B) Only Prometheus
C) Only Jaeger
D) Datadog and New Relic only

### 9. What is fault injection in Istio and what is it used for?
A) Injecting delays/abort errors via VirtualService `fault` field to test resilience (retry logic, circuit breakers, timeout handling)
B) Injecting bugs into application code for chaos engineering
C) Injecting network partitions at kernel level
D) Injecting fake metrics to test dashboards

### 10. What is the difference between STRICT and PERMISSIVE mTLS mode in PeerAuthentication?
A) STRICT: only mTLS allowed; PERMISSIVE: accepts both mTLS and plaintext (for migration)
B) STRICT: encrypts all traffic; PERMISSIVE: encrypts only ingress
C) STRICT: requires client certs; PERMISSIVE: optional client certs
D) No difference - both enforce mTLS

---

## Answers

| Question | Answer | Explanation |
|----------|--------|-------------|
| 1 | **A** | Control plane = Istiod (Pilot, Citadel, Galley merged); Data plane = Envoy sidecar proxies injected into each pod. |
| 2 | **A** | Istio's sidecar injector webhook watches for namespace label `istio-injection=enabled` or pod annotation `sidecar.istio.io/inject="true"` and patches pod spec. |
| 3 | **A** | mTLS = mutual authentication. Istio's Citadel (now in Istiod) acts as CA, issues workload certs (SPIFFE), SDS pushes certs/keys to Envoy without disk writes. |
| 4 | **B** | VirtualService `http:` → `route:` with multiple destinations + `weight:` for traffic splitting. DestinationRule defines subsets (`subset:` labels) for version routing. |
| 5 | **A** | VirtualService = *how* to route (match conditions, rewrite, redirect, fault, mirror). DestinationRule = *policies* for upstream (LB algorithm, circuit breaker, TLS, subsets). |
| 6 | **A** | `outlierDetection`: consecutive5xx, interval, baseEjectionTime, maxEjectionPercent. `connectionPool`: tcp/http limits. Envoy ejects endpoints exceeding thresholds. |
| 7 | **A** | IngressGateway = managed Envoy at mesh edge. Handles TLS termination, SNI routing, mTLS origination to internal services. |
| 8 | **A** | Istio exports Envoy stats to Prometheus (via `istio-telemetry`/`prometheus` addon), traces to Jaeger/Zipkin (via `tracing` config), access logs to stdout/Flue |
| 9 | **A** | `fault: { delay: { percentage: 50, fixedDelay: 5s }, abort: { percentage: 10, httpStatus: 500 } }` - tests client resilience without code changes. |
| 10 | **A** | STRICT = reject non-mTLS. PERMISSIVE = accept both (used during rollout). MIGRATE (deprecated) = same as PERMISSIVE. |

---

## Scoring

- **9-10**: Service Mesh Expert - Deep understanding of data/control plane, mTLS internals, traffic policies
- **7-8**: Service Mesh Practitioner - Solid; review circuit breaker config and fault injection syntax
- **5-6**: Service Mesh Learner - Good foundation; focus on VirtualService vs DestinationRule distinction
- **<5**: Beginner - Re-read GUIDE; deploy Istio locally with `istioctl install --set profile=demo`