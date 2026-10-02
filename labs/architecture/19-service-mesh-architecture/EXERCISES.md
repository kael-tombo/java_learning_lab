# Service Mesh Architecture Exercises

## Exercise 1: Istio Installation & Verification (Lab Task)

**Install** Istio in a Kind/k3d cluster and verify:

```bash
# 1. Create cluster
kind create cluster --name mesh-lab

# 2. Install Istio (demo profile)
istioctl install --set profile=demo -y

# 3. Enable sidecar injection for namespace
kubectl label namespace default istio-injection=enabled

# 4. Deploy sample app (Bookinfo)
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml
kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml
```

**Verify**:
1. `istioctl verify-install` — control plane healthy
2. `istioctl proxy-status` — all sidecars synced
3. `kubectl get pods` — each pod has 2 containers (app + istio-proxy)
4. Access Bookinfo via ingress gateway

**Deliverable**: Screenshots + `istioctl analyze` output (no errors)

---

## Exercise 2: mTLS Configuration & Verification (Config Task)

**Configure** mTLS modes and verify encryption:

### 2a: STRICT mTLS (mesh-wide)
```yaml
# peer-authentication-strict.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
```

### 2b: PERMISSIVE for legacy namespace
```yaml
# peer-authentication-permissive.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: legacy-permissive
  namespace: legacy
spec:
  mtls:
    mode: PERMISSIVE
```

**Verify**:
1. `istioctl authn tls-check <pod>.<namespace>` — shows mTLS status
2. Capture traffic with `tcpdump` — verify TLS handshake
3. `istioctl proxy-config secret <pod>` — check certs

**Test**: Deploy app in `legacy` namespace calling `default` namespace — should work in PERMISSIVE.

---

## Exercise 3: Traffic Management — Canary & Mirroring (Config Task)

**Deploy** two versions of a service and implement canary:

### 3a: Deploy v1 and v2
```yaml
# deployment-v1.yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: hello-v1, labels: { app: hello, version: v1 } }
spec:
  replicas: 2
  selector: { matchLabels: { app: hello, version: v1 } }
  template:
    metadata: { labels: { app: hello, version: v1 } }
    spec:
      containers:
      - name: hello
        image: kennethreitz/httpbin  # returns JSON with headers
        ports: [{ containerPort: 80 }]
---
# deployment-v2.yaml (same but version: v2, replicas: 1)
```

### 3b: DestinationRule with subsets
```yaml
# destination-rule.yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata: { name: hello }
spec:
  host: hello
  subsets:
  - name: v1
    labels: { version: v1 }
  - name: v2
    labels: { version: v2 }
  trafficPolicy:
    connectionPool:
      tcp: { maxConnections: 100 }
      http: { h2UpgradePolicy: UPGRADE, http1MaxPendingRequests: 100 }
    outlierDetection:
      consecutive5xxErrors: 3
      interval: 30s
      baseEjectionTime: 30s
```

### 3c: Canary VirtualService (10% to v2)
```yaml
# virtual-service-canary.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata: { name: hello }
spec:
  hosts: ["hello"]
  http:
  - route:
    - destination: { host: hello, subset: v1 }
      weight: 90
    - destination: { host: hello, subset: v2 }
      weight: 10
```

### 3d: Mirror traffic to v2 (shadow)
```yaml
# virtual-service-mirror.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata: { name: hello }
spec:
  hosts: ["hello"]
  http:
  - route:
    - destination: { host: hello, subset: v1 }
      weight: 100
    mirror:
      host: hello
      subset: v2
    mirrorPercentage:
      value: 100
```

**Test**:
1. `for i in {1..100}; do curl hello; done | grep version` — verify 90/10 split
2. Mirror: v2 receives traffic but responses discarded — check v2 logs

---

## Exercise 4: Resilience — Retry, Timeout, Circuit Breaker (Config Task)

**Configure** resilience policies for a flaky service:

```yaml
# virtual-service-resilience.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata: { name: flaky-service }
spec:
  hosts: ["flaky-service"]
  http:
  - match:
    - uri:
        prefix: "/api"
    route:
    - destination: { host: flaky-service }
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: connect-failure,refused-stream,unavailable,cancelled,retriable-status-codes
      retryRemoteLocalities: true
    timeout: 10s
    fault:
      delay:
        percentage:
          value: 10
        fixedDelay: 5s
      abort:
        percentage:
          value: 5
        httpStatus: 500
---
# destination-rule-cb.yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata: { name: flaky-service }
spec:
  host: flaky-service
  trafficPolicy:
    connectionPool:
      tcp: { maxConnections: 100 }
      http: { h2UpgradePolicy: UPGRADE, http1MaxPendingRequests: 100, http2MaxRequests: 1000 }
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 30
```

**Test with load**:
```bash
# Install hey
hey -n 1000 -c 50 http://flaky-service/api

# Observe: 
# - Retries kick in for 5xx
# - Timeout caps at 10s
# - Circuit breaker ejects unhealthy pods
# - Fault injection adds latency/errors
```

**Metrics to check**:
- `istio_requests_total{destination_service="flaky-service",response_code=~"5.."}`
- `istio_outlier_detection_ejections_total`

---

## Exercise 5: Authorization Policies (Security Task)

**Implement** zero-trust network policies:

### 5a: Default deny all
```yaml
# authz-deny-all.yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata: { name: deny-all, namespace: prod }
spec:
  selector: {}  # applies to all workloads in namespace
  action: DENY
  rules: []  # empty = deny all
```

### 5b: Allow payment-service → billing-service
```yaml
# authz-payment-to-billing.yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata: { name: payment-to-billing, namespace: prod }
spec:
  selector:
    matchLabels:
      app: billing-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/prod/sa/payment-service"]
    to:
    - operation:
        paths: ["/charge", "/refund"]
        methods: ["POST"]
```

### 5c: JWT validation for external ingress
```yaml
# request-auth-jwt.yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata: { name: jwt-auth, namespace: prod }
spec:
  selector:
    matchLabels:
      app: api-gateway
  jwtRules:
  - issuer: "https://auth.company.com"
    audiences: ["api.company.com"]
    jwksUri: "https://auth.company.com/.well-known/jwks.json"
---
# authz-require-jwt.yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata: { name: require-jwt, namespace: prod }
spec:
  selector:
    matchLabels:
      app: api-gateway
  action: ALLOW
  rules:
  - from:
    - source:
        requestPrincipals: ["*"]
```

**Test**:
1. Call billing-service from payment-service (same ns) — 200 OK
2. Call billing-service from unknown-service — 403 Forbidden
3. Call api-gateway without JWT — 401 Unauthorized
4. Call with valid JWT — 200 OK

---

## Exercise 6: Observability — Tracing & Metrics (Integration Task)

**Deploy** Jaeger and configure tracing:

```bash
# Install Jaeger
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/jaeger.yaml

# Configure mesh for sampling
kubectl apply -f - <<EOF
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-default
  namespace: istio-system
spec:
  tracing:
  - providers:
    - name: jaeger
    randomSamplingPercentage: 10.0  # 10% sampling
EOF
```

**Generate traffic** and verify traces in Jaeger UI:
1. `kubectl port-forward -n istio-system svc/jaeger 16686:16686`
2. Open http://localhost:16686
3. Search for traces from Bookinfo or your app
4. Verify: spans for ingress → service → service → DB

**Custom metrics** — add request size histogram:
```yaml
# telemetry-custom-metrics.yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: custom-metrics
  namespace: prod
spec:
  metrics:
  - providers:
    - name: prometheus
    overrides:
    - match:
        metric: REQUEST_SIZE
        mode: CLIENT_AND_SERVER
      metric: REQUEST_SIZE
      tags:
        request_size_bucket:
          value: "histogram_bucket"
```

---

## Exercise 7: Multi-Cluster Setup (Advanced Task)

**Set up** two Kind clusters and connect via Istio multi-primary:

```bash
# Cluster 1
kind create cluster --name cluster1
istioctl install --set profile=default -y --context kind-cluster1
istioctl x create-remote-secret --context kind-cluster1 --name=cluster1 | kubectl apply -f - --context kind-cluster2

# Cluster 2
kind create cluster --name cluster2
istioctl install --set profile=default -y --context kind-cluster2
istioctl x create-remote-secret --context kind-cluster2 --name=cluster2 | kubectl apply -f - --context kind-cluster1

# Enable cross-cluster service discovery
kubectl apply -f - <<EOF --context kind-cluster1
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: hello-cluster2
  namespace: default
spec:
  hosts:
  - hello.default.svc.cluster2.local
  location: MESH_INTERNAL
  ports:
  - number: 80
    name: http
    protocol: HTTP
  resolution: DNS
EOF
```

**Test**: Deploy `hello` in cluster2, call from cluster1 using FQDN `hello.default.svc.cluster2.local`.

**Verify**:
- `istioctl proxy-config endpoints <pod> --cluster cluster1` — shows cluster2 endpoints
- Trace shows cross-cluster hops

---

## Exercise 8: Ambient Mesh (Sidecar-less) (Exploration Task)

**Enable** Istio Ambient mode (no sidecars):

```bash
# Install Istio with ambient profile
istioctl install --set profile=ambient -y

# Add namespace to ambient
kubectl label namespace default istio.io/dataplane-mode=ambient

# Deploy waypoint proxy for namespace
istioctl waypoint apply --namespace default
```

**Compare** resource usage:
| Metric | Sidecar | Ambient (ztunnel + waypoint) |
|--------|---------|------------------------------|
| Pods per node | N+1 | N + 1 waypoint per ns |
| Memory per pod | +50MB (Envoy) | +0MB (ztunnel shared) |
| CPU per pod | +50m | +0m |
| mTLS | Per-pod | Per-node (ztunnel) |

**Test**: Deploy app in ambient namespace, verify mTLS works, check ztunnel logs.

---

## Exercise 9: Debugging Workshop (Troubleshooting Task)

**Scenario**: Service `orders` returning 503 intermittently.

**Debug steps** (run and document):

1. **Check sidecar status**:
   ```bash
   istioctl proxy-status | grep orders
   ```

2. **Check config sync**:
   ```bash
   istioctl proxy-config listener <orders-pod> -n prod -o json | jq '.[] | select(.name | contains("outbound"))'
   ```

3. **Check endpoints**:
   ```bash
   istioctl proxy-config endpoints <orders-pod> -n prod
   ```

4. **Check authz**:
   ```bash
   istioctl x authz check <orders-pod> -n prod
   ```

5. **Check metrics**:
   ```bash
   # Port-forward Prometheus
   kubectl port-forward -n istio-system svc/prometheus 9090
   # Query: istio_requests_total{destination_service=~"orders.*",response_code=~"5.."}
   ```

6. **Capture Envoy config dump**:
   ```bash
   istioctl proxy-config all <orders-pod> -n prod -o json > orders-config.json
   ```

**Root cause scenarios to simulate**:
- DestinationRule subsets don't match pod labels
- AuthorizationPolicy missing principal
- Circuit breaker ejected all endpoints
- mTLS mode mismatch (STRICT vs PERMISSIVE)

---

## Exercise 10: Performance Benchmark (Benchmark Task)

**Benchmark** mesh overhead vs baseline:

**Setup**:
- 2 namespaces: `baseline` (no injection), `meshed` (injection=enabled)
- Deploy identical HTTP service (e.g., `ghcr.io/istio/test-server`)
- Client: `hey` or `wrk`

**Test matrix**:
| Scenario | Baseline (ms) | Meshed (ms) | Overhead |
|----------|---------------|-------------|----------|
| p50 latency | | | |
| p99 latency | | | |
| Throughput (RPS) | | | |
| CPU (client) | | | |
| CPU (server) | | | |
| Memory (sidecar) | N/A | | |

**Run**:
```bash
# Baseline
hey -n 10000 -c 100 http://baseline-svc/

# Meshed
hey -n 10000 -c 100 http://meshed-svc/
```

**Analyze**: Is overhead acceptable for your use case? What optimizations help?

---

## Grading Rubric

| Exercise | Points | Criteria |
|----------|--------|----------|
| 1. Installation | 10 | Clean install, Bookinfo works |
| 2. mTLS | 15 | STRICT/PERMISSIVE verified |
| 3. Canary/Mirror | 15 | Weighted routing + mirroring work |
| 4. Resilience | 15 | Retry/timeout/CB configured, tested |
| 5. AuthZ | 15 | Zero-trust policies enforced |
| 6. Observability | 10 | Traces visible, custom metrics |
| 7. Multi-cluster | 15 | Cross-cluster calls work |
| 8. Ambient | 10 | Sidecar-less mode functional |
| 9. Debugging | 15 | Root causes identified |
| 10. Benchmark | 10 | Data collected, analyzed |

**Total**: 130 points