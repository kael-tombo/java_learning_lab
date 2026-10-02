# Service Mesh Deep Dive - Flashcards

Spaced repetition format: **Question** → **Answer**

---

## Architecture

**Istio control plane components (merged into Istiod)?**
→ **Pilot**: Service discovery, traffic management config → xDS to Envoy
→ **Citadel**: Certificate authority, workload identity (SPIFFE), cert rotation
→ **Galley** (deprecated): Config validation, processing (now in Istiod)

**What is xDS?**
→ Envoy discovery APIs: **LDS** (Listener), **RDS** (Route), **CDS** (Cluster), **EDS** (Endpoint), **SDS** (Secret). Istiod pushes config via gRPC streams.

**Envoy sidecar injection flow?**
1. Pod created → 2. MutatingWebhook intercepts → 3. Adds `istio-init` (or CNI) + `istio-proxy` containers → 4. `istio-init` runs `iptables` to redirect all traffic to Envoy (port 15006) → 5. Envoy starts, fetches config from Istiod via xDS

**What is SDS (Secret Discovery Service)?**
→ xDS API for secrets. Envoy requests certs/keys from Istiod via SDS → Istiod returns SPIFFE cert/key → Envoy uses for mTLS. No secrets on disk, auto-rotation.

**Ambient Mesh (sidecarless)?**
→ New mode: **ztunnel** (per-node L4 proxy) + **waypoint** (per-namespace L7 proxy). No per-pod sidecar. Reduces resource overhead. Still alpha/beta.

---

## mTLS

**SPIFFE ID format?**
→ `spiffe://<trust-domain>/ns/<namespace>/sa/<serviceaccount>` e.g., `spiffe://cluster.local/ns/default/sa/default`

**PeerAuthentication modes?**
→ `STRICT`: Only mTLS allowed (reject plaintext)
→ `PERMISSIVE`: Accept both mTLS and plaintext (migration)
→ `DISABLE`: No mTLS (legacy)

**DestinationRule TLS settings for mTLS?**
```yaml
trafficPolicy:
  tls:
    mode: ISTIO_MUTUAL  # use Istio-managed certs
    # or SIMPLE, MUTUAL (custom certs), DISABLE
```

**How to verify mTLS is working?**
→ `istioctl authn tls-check <pod>.<namespace>` → shows CONNECTED (mTLS) or CONNECTED (PLAINTEXT)
→ `istioctl x authz check <pod>` → authorization check
→ Envoy admin `/stats` → `ssl.handshake` counters

---

## Traffic Management

**VirtualService vs DestinationRule?**
→ **VirtualService**: Routing rules (match: uri, headers, method → route: destination, weight, rewrite, timeout, retry, fault, mirror)
→ **DestinationRule**: Upstream policies (subsets, loadBalancer, connectionPool, outlierDetection, tls)

**Subsets in DestinationRule?**
```yaml
subsets:
- name: v1
  labels:
    version: v1
- name: v2
  labels:
    version: v2
```
Used in VirtualService `route: - destination: host: mysvc, subset: v1`

**Traffic splitting (canary)?**
```yaml
# VirtualService
http:
- route:
  - destination:
      host: mysvc
      subset: v1
    weight: 90
  - destination:
      host: mysvc
      subset: v2
    weight: 10
```

**Request routing match conditions?**
→ `uri: { exact: "/api", prefix: "/api", regex: ".*" }`
→ `headers: { end-user: { exact: "john" } }`
→ `method: { exact: "GET" }`
→ `sourceLabels: { app: "client" }`

**Timeouts & Retries?**
```yaml
timeout: 10s
retries:
  attempts: 3
  perTryTimeout: 2s
  retryOn: "connect-failure,refused-stream,unavailable,cancelled,retriable-status-codes"
  retryRemoteLocalities: true
```

**Fault Injection?**
```yaml
fault:
  delay:
    percentage:
      value: 50.0
    fixedDelay: 5s
  abort:
    percentage:
      value: 10.0
    httpStatus: 503
```

**Traffic Mirroring (shadow)?**
```yaml
route:
- destination:
    host: mysvc
    subset: v1
  weight: 100
mirror:
  destination:
    host: mysvc
    subset: v2
mirrorPercentage:
  value: 100.0
```

---

## Resilience

**Circuit Breaker (DestinationRule)?**
```yaml
trafficPolicy:
  connectionPool:
    tcp:
      maxConnections: 100
    http:
      h2UpgradePolicy: UPGRADE
      http1MaxPendingRequests: 100
      http2MaxRequests: 1000
  outlierDetection:
    consecutive5xxErrors: 5
    interval: 30s
    baseEjectionTime: 30s
    maxEjectionPercent: 50
    minHealthPercent: 30
```

**Outlier Detection = Circuit Breaker**
→ Tracks 5xx errors → ejects endpoint for `baseEjectionTime` → max `maxEjectionPercent` of endpoints ejected → requires `minHealthPercent` healthy to accept traffic

**Load Balancing Algorithms?**
→ `ROUND_ROBIN` (default), `LEAST_REQUEST`, `RANDOM`, `PASSTHROUGH` (use caller's LB), `CONSISTENT_HASH` (session affinity)

---

## Gateways

**Gateway vs VirtualService?**
→ **Gateway**: L4/L6 config (port, protocol, TLS cert, SNI) - *edge of mesh*
→ **VirtualService**: L7 routing *attached to Gateway* via `gateways: ["my-gateway"]`

**Ingress Gateway Example:**
```yaml
# Gateway
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: my-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: my-tls-secret
    hosts:
    - "app.example.com"

# VirtualService
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  gateways: ["my-gateway"]
  hosts: ["app.example.com"]
  http:
  - route:
    - destination:
        host: myapp
```

**Egress Gateway?**
→ Control outbound traffic: `spec.servers[].port.protocol: TLS`, `hosts: ["external-api.com"]` → route via dedicated egress gateway pods for compliance/audit.

---

## Observability

**Key Metrics (Prometheus)?**
→ `istio_requests_total` (counter, by response_code, source/dest workload)
→ `istio_request_duration_milliseconds` (histogram, latency)
→ `istio_tcp_sent_bytes_total`, `istio_tcp_received_bytes_total`
→ `envoy_cluster_upstream_rq_pending_active` (pending requests)

**Distributed Tracing?**
→ Envoy generates trace context (`x-request-id`, `x-b3-traceid`) → propagates via headers → sends to Jaeger/Zipkin → Istio adds mesh metadata (source/dest workload, namespace)

**Access Logs?**
→ `telemetry.v1alpha1` or `meshConfig.accessLogFile` / `accessLogFormat` → JSON or text → stdout or file → Fluentd/Filebeat → Elasticsearch/Loki

**Kiali?**
→ Visualizes service graph, mTLS status, traffic flows, metrics, traces. `istioctl dashboard kiali`

---

## Authorization

**AuthorizationPolicy?**
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: myapp-authz
spec:
  selector:
    matchLabels:
      app: myapp
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/frontend/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
  - from:
    - source:
        namespaces: ["monitoring"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/metrics"]
```

**Action: ALLOW (default) | DENY | AUDIT**
→ AUDIT: logs but doesn't enforce (dry-run)

---

## Commands Quick Reference

| Task | Command |
|------|---------|
| Install Istio | `istioctl install --set profile=default -y` |
| Enable injection | `kubectl label ns default istio-injection=enabled` |
| Check mTLS | `istioctl authn tls-check <pod>.<ns>` |
| Analyze config | `istioctl analyze` |
| View proxy config | `istioctl proxy-config routes <pod>.<ns>` |
| View proxy clusters | `istioctl proxy-config clusters <pod>.<ns>` |
| View proxy listeners | `istioctl proxy-config listeners <pod>.<ns>` |
| View proxy endpoints | `istioctl proxy-config endpoints <pod>.<ns>` |
| Dashboard | `istioctl dashboard kiali / grafana / jaeger / prometheus` |
| Generate manifest | `istioctl manifest generate --set profile=demo` |
| Upgrade | `istioctl upgrade --set profile=default` |
| Uninstall | `istioctl uninstall --purge -y` |