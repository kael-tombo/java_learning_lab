# Service Mesh Deep Dive - Exercises

Hands-on tasks for Istio service mesh: traffic management, mTLS, observability, resilience.

---

## Prerequisites

- Kubernetes cluster (kind, k3d, minikube, or cloud)
- `kubectl`, `helm`, `istioctl` installed
- Sample app: `httpbin` + `sleep` (included in Istio samples)

---

## Exercise 1: Install Istio with Demo Profile

```bash
# Download Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH

# Install with demo profile (includes ingress/egress gateways, Kiali, Prometheus, Grafana, Jaeger)
istioctl install --set profile=demo -y

# Verify
istioctl verify-install
kubectl get pods -n istio-system

# Enable sidecar injection for default namespace
kubectl label namespace default istio-injection=enabled
```

**✅ Verify**: `istioctl version` shows client/control plane versions; pods in istio-system Running.

---

## Exercise 2: Deploy Bookinfo Sample Application

```bash
# Deploy Bookinfo (microservices: productpage, details, reviews v1/v2/v3, ratings)
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml

# Verify pods
kubectl get pods -l app=productpage
kubectl get pods -l app=details
kubectl get pods -l app=reviews
kubectl get pods -l app=ratings

# Deploy ingress gateway for external access
kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml

# Get ingress gateway URL
export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].port}')
export GATEWAY_URL=$INGRESS_HOST:$INGRESS_PORT

# Test
curl -s -o /dev/null -w "%{http_code}" http://$GATEWAY_URL/productpage
```

**✅ Verify**: Bookinfo productpage accessible at `http://$GATEWAY_URL/productpage`.

---

## Exercise 3: Configure Traffic Splitting (Canary)

**Goal**: Route 90% to reviews:v1, 10% to reviews:v2.

```bash
# 1. Define subsets for reviews versions
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
  - name: v3
    labels:
      version: v3
EOF

# 2. Create VirtualService with traffic split
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
        subset: v1
      weight: 90
    - destination:
        host: reviews
        subset: v2
      weight: 10
EOF

# 3. Test - refresh productpage multiple times
for i in {1..20}; do curl -s http://$GATEWAY_URL/productpage | grep -o "Review.*Reviewer" | head -1; done
# Should see mostly v1 (black stars), occasionally v2 (red stars)
```

**✅ Verify**: `istioctl proxy-config routes deploy/productpage -n default` shows weighted routes.

---

## Exercise 4: Enable mTLS (STRICT Mode)

```bash
# 1. Check current mTLS status
istioctl authn tls-check deploy/productpage.default

# 2. Enable STRICT mTLS for entire mesh
kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
EOF

# 3. Verify mTLS is enforced
istioctl authn tls-check deploy/productpage.default
# Should show: CONNECTED (mTLS) for all connections

# 4. Test app still works
curl -s -o /dev/null -w "%{http_code}" http://$GATEWAY_URL/productpage
```

**✅ Verify**: All service-to-service connections show mTLS; app still functional.

---

## Exercise 5: Configure Circuit Breaker

**Goal**: Protect reviews service from cascade failures.

```bash
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews-cb
spec:
  host: reviews
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
    outlierDetection:
      consecutive5xxErrors: 3
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 30
EOF

# Test: Simulate failing requests to trigger ejection
# (Deploy a failing version or use fault injection - see Exercise 7)
```

**✅ Verify**: `istioctl proxy-config clusters deploy/productpage.default -n default -o json | jq '.[] | select(.name=="outbound|9080||reviews.default.svc.cluster.local") | .outlier_detection'`

---

## Exercise 6: Implement Request Timeout & Retry

```bash
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ratings
spec:
  hosts:
  - ratings
  http:
  - route:
    - destination:
        host: ratings
    timeout: 5s
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: "connect-failure,refused-stream,unavailable,cancelled,retriable-status-codes"
EOF
```

**✅ Verify**: `istioctl proxy-config routes deploy/reviews-v1.default -n default -o json | jq '.[].route[].route_timeout, .[].route[].retry_policy'`

---

## Exercise 7: Fault Injection for Resilience Testing

**Goal**: Inject 50% 5s delay and 10% 503 errors to ratings service.

```bash
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ratings-fault
spec:
  hosts:
  - ratings
  http:
  - fault:
      delay:
        percentage:
          value: 50.0
        fixedDelay: 5s
      abort:
        percentage:
          value: 10.0
        httpStatus: 503
    route:
    - destination:
        host: ratings
EOF

# Test: Observe productpage latency increase and errors
for i in {1..10}; do time curl -s -o /dev/null -w "%{http_code}\n" http://$GATEWAY_URL/productpage; done

# Remove fault after testing
kubectl delete virtualservice ratings-fault
```

**✅ Verify**: Productpage shows increased latency; circuit breaker (Exercise 5) may eject ratings pods.

---

## Exercise 8: Traffic Mirroring (Shadow Traffic)

**Goal**: Mirror 100% of production traffic to v3 for testing without user impact.

```bash
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-mirror
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
        subset: v1
      weight: 100
    mirror:
      destination:
        host: reviews
        subset: v3
    mirrorPercentage:
      value: 100.0
EOF

# Check v3 receives mirrored traffic (no response sent to client)
kubectl logs -l app=reviews,version=v3 -c istio-proxy | tail -20
```

**✅ Verify**: v3 logs show incoming requests; productpage responses unchanged.

---

## Exercise 9: Configure Authorization Policy

**Goal**: Allow only productpage to call reviews; allow monitoring to scrape metrics.

```bash
kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: reviews-authz
  namespace: default
spec:
  selector:
    matchLabels:
      app: reviews
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/bookinfo-productpage"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/reviews/*"]
  - from:
    - source:
        namespaces: ["istio-system", "monitoring"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/metrics", "/stats"]
EOF

# Test: Try calling reviews directly from sleep pod (should fail)
kubectl exec -it deploy/sleep -c sleep -- curl -s http://reviews:9080/reviews/1
# Should return 403 RBAC: access denied
```

**✅ Verify**: Direct calls blocked; productpage → reviews still works.

---

## Exercise 10: Observability - Metrics, Tracing, Logs

### Prometheus Metrics
```bash
# Port-forward Prometheus
kubectl -n istio-system port-forward svc/prometheus 9090:9090 &

# Query key metrics in Prometheus UI (http://localhost:9090)
# istio_requests_total{destination_service="reviews.default.svc.cluster.local"}
# istio_request_duration_milliseconds_bucket{destination_service=~"reviews.*"}
```

### Distributed Tracing (Jaeger)
```bash
# Port-forward Jaeger
kubectl -n istio-system port-forward svc/tracing 16686:16686 &

# Open http://localhost:16686
# Search service: productpage.default
# View trace spans: productpage → reviews → ratings
```

### Access Logs
```bash
# View Envoy access logs for productpage
kubectl logs -l app=productpage -c istio-proxy -f | jq .

# Or use Kiali for unified view
kubectl -n istio-system port-forward svc/kiali 20001:20001 &
# Open http://localhost:20001 (admin/admin)
```

---

## Exercise 11: Egress Control (External Service Access)

**Goal**: Control outbound traffic to external APIs.

```bash
# 1. Create ServiceEntry for external service
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: httpbin-ext
spec:
  hosts:
  - httpbin.org
  location: MESH_EXTERNAL
  ports:
  - number: 443
    name: https
    protocol: TLS
  resolution: DNS
EOF

# 2. Test from sleep pod (should work via egress gateway)
kubectl exec -it deploy/sleep -c sleep -- curl -s https://httpbin.org/get

# 3. Restrict to egress gateway only
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: egress-gateway-tls
spec:
  host: istio-egressgateway.istio-system.svc.cluster.local
  subsets:
  - name: httpbin
    trafficPolicy:
      loadBalancer:
        simple: ROUND_ROBIN
      portLevelSettings:
      - port:
          number: 443
        tls:
          mode: ISTIO_MUTUAL
          sni: httpbin.org
EOF
```

---

## Exercise 12: Upgrade Istio (Canary Upgrade Pattern)

```bash
# 1. Download new version
export NEW_VERSION=1.22.0
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=$NEW_VERSION sh -
cd istio-$NEW_VERSION
export PATH=$PWD/bin:$PATH

# 2. Canary upgrade - install new control plane with revision tag
istioctl install --set profile=default --set revision=1-22 -y

# 3. Migrate namespaces gradually
kubectl label namespace default istio.io/rev=1-22 --overwrite
# Pods restart with new sidecar version

# 4. Verify
istioctl proxy-status
kubectl get pods -n default -o wide

# 5. Complete upgrade (remove old)
istioctl uninstall --revision=default -y
```

---

## Challenge Exercises

| # | Challenge | Description |
|---|-----------|-------------|
| 1 | **WASM Plugin** | Write Envoy WASM filter (Rust/Go) for custom auth; deploy via WasmPlugin CRD |
| 2 | **Multi-Cluster Mesh** | Join two clusters via `istioctl x create-remote-secret`; configure cross-cluster ServiceEntries |
| 3 | **Ambient Mesh** | Enable ambient mode (`istioctl install --set profile=ambient`); deploy ztunnel + waypoint |
| 4 | **Custom Metrics** | Add Prometheus adapter for HPA based on `istio_requests_total` per service |
| 5 | **Security Hardening** | Implement JWT validation via RequestAuthentication; restrict workload identities |

---

## Validation Checklist

- [ ] Install Istio with demo profile
- [ ] Deploy Bookinfo and verify external access
- [ ] Configure traffic splitting (VirtualService + DestinationRule subsets)
- [ ] Enable mesh-wide STRICT mTLS
- [ ] Configure circuit breaker with outlier detection
- [ ] Set timeouts and retries for upstream calls
- [ ] Inject faults (delay/abort) to test resilience
- [ ] Implement traffic mirroring for shadow testing
- [ ] Write AuthorizationPolicy for service-to-service auth
- [ ] Query Prometheus metrics, view Jaeger traces, Kiali graph
- [ ] Control egress traffic with ServiceEntry + Egress Gateway
- [ ] Perform canary control plane upgrade

---

## Resources

- [Istio Documentation](https://istio.io/latest/docs/)
- [Istio Tasks](https://istio.io/latest/docs/tasks/)
- [Envoy Proxy Docs](https://www.envoyproxy.io/docs/envoy/latest/)
- [xDS Protocol](https://www.envoyproxy.io/docs/envoy/latest/api-docs/xds_protocol)
- [SPIFFE/SPIRE](https://spiffe.io/)
- [Kiali User Guide](https://kiali.io/documentation/)