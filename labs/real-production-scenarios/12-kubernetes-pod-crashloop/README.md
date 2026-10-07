# Lab 12: Kubernetes Pod CrashLoop — Production Deployment Failure

## Situation Overview

**Scenario**: Google Kubernetes Engine (GKE) — pod crashlooping after deployment to production

**Severity**: P0 (Critical) / SEV1

**Impact Assessment**:
- Production deployment of order-processing service (v3.2.1) causes immediate pod crashlooping
- 47 out of 50 pod replicas in CrashLoopBackOff within 3 minutes of deployment
- Order processing pipeline completely stalled — 12,000+ pending orders accumulating
- Downstream consumers (inventory, payment, shipping) unable to process
- Revenue loss estimated at $84,000/hour during peak hours (09:00–17:00 UTC)
- Customer-facing "order pending" status causing support ticket surge (850+ tickets/hour)
- Incident duration: 2 hours 38 minutes (10:23 UTC — 13:01 UTC)

**Affected Systems**:
- `order-processor` Deployment in `production` namespace (GKE cluster: prod-us-east-1)
- Downstream: `payment-service`, `inventory-service`, `shipping-service`
- Upstream: `api-gateway`, `order-api`
- Monitoring: Prometheus, Grafana, metrics-server
- CI/CD: ArgoCD deployment pipeline (v3.2.1 rolled out automatically)

**Detection**: ArgoCD shows `Degraded` status for `order-processor` deployment. Prometheus alert `KubePodCrashLooping` fires within 90 seconds of deployment rollout. Grafana dashboard shows CPU throttling > 200% of limit.

**Business Context**: The order-processing service handles $3.1M in daily transaction volume. The crashlooping was triggered by a JVM heap memory regression introduced in v3.2.1 (increased thread pool size from 200 to 500 threads without corresponding heap increase). The deployment was rolled out automatically via ArgoCD's automated sync policy during peak business hours.

**Engineering Teams Involved**:
- Platform SRE (Kubernetes cluster management, pod diagnostics)
- Java Application Team (code review, heap analysis)
- CI/CD Team (ArgoCD rollback, deployment pipeline fixes)
- Database Team (connection pool impact)
- Observability Team (metrics, tracing, alert tuning)

## References

1. Google Kubernetes Engine Documentation — Pod Lifecycle — (link removed)
2. Google SRE Book — Chapter 6: Monitoring Distributed Systems — https://sre.google/sre-book/monitoring-distributed-systems/
3. Netflix Tech Blog — Container Resource Tuning — https://netflixtechblog.com/container-resource-tuning
4. Datadog Blog — Kubernetes Pod CrashLoopBackOff — (link removed)
5. Kubernetes SIG Recommendations — Resource QoS — https://kubernetes.io/docs/tasks/configure-pod-container/quality-service-pod/
6. Java Memory Management in Containers — https://www.oreilly.com/library/view/java-performance-in/9781492056579/
7. Prometheus Community — Kubernetes Mixin — https://github.com/prometheus-community/helm-charts
8. cAdvisor Documentation — https://github.com/google/cadvisor

## Key Metrics

| Metric | Value | Normal Range |
|--------|-------|-------------|
| Pod restart count | 15+ per pod | < 1 per hour |
| CPU throttling | 450% of limit | < 80% of limit |
| Memory usage (pre-OOM) | 2.1 GB / 2 GB limit | < 1.5 GB |
| JVM heap usage | 1.8 GB / 2 GB limit | < 1.2 GB |
| Order processing rate | 0/min | 1,200/min |
| Time to detect | 90 seconds (auto) | < 1 minute |
| Time to rollback | 8 minutes | < 5 minutes target |
| Time to resolve | 2h 38m | < 30 minutes target |
| Number of affected deployments | 47 of 50 | 0 |

## Detailed Impact Analysis

### Pod Failure Timeline

| Time (Relative) | Event | Pods Affected | Cumulative Impact |
|----------------|-------|---------------|-------------------|
| t+0s | Deployment v3.2.1 rolled out | 0/50 | Rollout started |
| t+5s | First OOMKilled (memory exceeds 2GB limit) | 3/50 | 6% affected |
| t+10s | Liveness probe fails (JVM not ready) | 12/50 | 24% affected |
| t+15s | CrashLoopBackOff exponential backoff | 28/50 | 56% affected |
| t+20s | All pods in crashloop | 47/50 | 94% affected |
| t+30s | Monitoring alert fires | 47/50 | 100% affected |
| t+60s | Remaining 3 pods also crashloop | 50/50 | Complete outage |
| t+8m | Rollback to v3.2.0 initiated | 50/50 | Rollback starts |
| t+12m | First v3.2.0 pods healthy | 12/50 | 24% recovered |
| t+15m | All v3.2.0 pods healthy | 50/50 | Fully recovered |

### Resource Utilization Before Failure

| Metric | v3.2.0 (Working) | v3.2.1 (Failing) | Delta |
|--------|-----------------|-----------------|-------|
| Memory usage (steady) | 1.2 GB | 2.1 GB | +75% |
| Memory usage (peak) | 1.5 GB | 2.8 GB (OOM) | +87% |
| CPU usage (steady) | 0.8 cores | 1.4 cores | +75% |
| CPU throttling | 5% | 450% | +9,000% |
| Thread count | 200 | 500 | +150% |
| Thread stack memory | 400 MB | 1,000 MB | +150% |
| Heap usage | 800 MB | 1,200 MB | +50% |
| GC pause time | 50ms | 500ms | +900% |
| Startup time | 30s | 45s | +50% |

### Pod Lifecycle Analysis

The lifecycle of a v3.2.1 pod under the faulty configuration:

```
t=0: Pod scheduled on node (us-east-1c)
t=1: Container starts, JVM initializes
    - Load classes (15,000+ classes)
    - JIT compilation begins
    - Spring context initialization
    - Thread pool created with 500 threads
t=5: Memory usage: 1.5 GB (75% of 2 GB limit)
    - First liveness probe → connection refused (JVM not ready)
t=10: Memory usage: 1.8 GB (90% of limit)
    - GC pressure: Full GC every 2 seconds
    - Second liveness probe → connection refused
t=15: Memory usage: 2.0 GB (100% of limit)
    - Third liveness probe → connection refused
    - Failure threshold reached (3)
t=20: kubelet kills pod (liveness probe failure)
    - Also: cgroup OOM killer triggered at 2.0 GB
t=21: Pod restarts (CrashLoopBackOff)
    - Exponential backoff: 10s, 20s, 40s, 80s, 160s...
t=35: Pod restarts again (backoff expired)
    - Same cycle repeats
```

### Probe Timing Analysis

The liveness probe timing guaranteed failure:

```
Probe Configuration:
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
  Time until kill = 5 + (3 × 5) = 20 seconds

JVM Startup Profile:
  Class loading: 15 seconds
  JIT compilation: 10 seconds
  Spring context init: 12 seconds
  Health endpoint registration: 5 seconds
  First healthy response available: 42 seconds
  Full startup completion: 45 seconds

Gap: 45s (required) - 20s (allowed) = 25s deficit
```

### Comparison: With vs Without Startup Probe

| Aspect | Without Startup Probe (Before) | With Startup Probe (After) |
|--------|-------------------------------|----------------------------|
| Probe type | livenessProbe only | startupProbe + livenessProbe |
| startupProbe | N/A | initialDelay: 5, period: 5, failures: 12 |
| Max startup time allowed | 20 seconds | 65 seconds |
| JVM startup time | 45 seconds | 45 seconds |
| Prevents premature kill | No | Yes |
| OOMKilled prevention | No (separate issue) | No (separate issue) |
| Rollout success rate | 0% (before fix) | 100% (after fix) |
| Deployment confidence | Low | High |

### Memory Allocation Breakdown

```
Pod Memory Allocation (2 GB limit):
  ┌─────────────────────────────────┐
  │ Java Heap (-Xmx1200m)   1,200 MB│ 60%
  ├─────────────────────────────────┤
  │ Thread Stacks (500 × 1MB) 500 MB│ 25%
  ├─────────────────────────────────┤
  │ Metaspace                  200 MB│ 10%
  ├─────────────────────────────────┤
  │ Code Cache                   48 MB│ 2.4%
  ├─────────────────────────────────┤
  │ Direct Buffers               32 MB│ 1.6%
  ├─────────────────────────────────┤
  │ Socket Buffers               16 MB│ 0.8%
  ├─────────────────────────────────┤
  │ JIT Compiler Overhead         4 MB│ 0.2%
  └─────────────────────────────────┘
  Total: 2,000 MB = 2 GB (AT LIMIT)

With 500 threads, native overhead alone consumes 500 MB + metaspace 200 MB + other 100 MB = 800 MB.
Combined with 1,200 MB heap = 2,000 MB = exactly at limit.
Any GC overhead or temporary allocation → OOM.
```

### Resource Limit Recommendation

Based on profiling, the correct resource configuration for this workload:

| Resource | Old Value | New Value | Rationale |
|----------|-----------|-----------|-----------|
| Memory request | 1 GB | 2 GB | 50% of limit for scheduling |
| Memory limit | 2 GB | 4 GB | Heap (1.2 GB) + Native (1 GB) + Headroom (1.8 GB) |
| CPU request | 500m | 1 | Guaranteed CPU for GC and JIT |
| CPU limit | 2 | 4 | Allow burst for startup and GC |
| Heap (-Xmx) | 1.2 GB | 2 GB | 50% of container limit |
| Metaspace | 200 MB | 256 MB | With 25% headroom |
| Thread stack | 1 MB | 512 KB | Reduce for 500 threads |
| Direct memory | Default | 64 MB | Explicit configuration |

### Deployment Strategy Comparison

| Strategy | Risk Level | Time to Detect | Time to Recover | User Impact |
|----------|-----------|---------------|-----------------|-------------|
| Direct apply (Before) | High | 90s | 15 min (rollback) | 100% outage |
| Canary 20% → 50% → 100% | Low | 30s | 2 min | 20% max |
| Blue/Green | Low | 30s | 30s | Zero (instant switch) |
| Rolling update (25% max surge) | Medium | 60s | 5 min | 25% degradation |
| A/B testing | Low | 30s | 30s | Segmented users |

## Lessons Learned

1. **Resource limits too low**: The container's memory limit (2 GB) was set based on v3.0 profiling, but v3.2.1 increased thread pool size by 150%, causing OOMKilled by cgroup.

2. **Liveness probe too strict**: The liveness probe had `initialDelaySeconds: 5` and `periodSeconds: 5`, causing the probe to kill pods before JVM warmup completed (JIT compilation takes ~30 seconds).

3. **No startup probe**: The deployment lacked a `startupProbe`, which would have allowed the JVM to initialize before liveness checks began.

4. **No canary deployment**: ArgoCD's automated sync applied the change to all 50 pods simultaneously — no gradual rollout.

5. **CPU throttling blind spot**: Metrics showed high CPU usage but the team hadn't configured CPU throttling alerts (container_cpu_cfs_throttled_seconds_total).

6. **No resource profiling CI step**: The CI pipeline ran unit tests but didn't include resource profiling (memory, CPU) to detect regressions.

7. **Missing JVM container flags**: The JVM was not configured with `-XX:+UseContainerSupport` or `-XX:MaxRAMPercentage`, causing it to ignore cgroup limits.

8. **No pre-deployment load testing**: The thread pool change was deployed without any load testing to validate resource requirements.

9. **Single-region deployment**: All pods deployed to a single GKE cluster with no cross-region redundancy.

10. **No PodDisruptionBudget**: The deployment lacked PDB to ensure minimum available pods during rollout.

### Appendix A: GKE Cluster Information

| Property | Value |
|----------|-------|
| Cluster name | prod-us-east-1 |
| Kubernetes version | 1.28.7-gke.123400 |
| Node count | 12 |
| Node type | e2-standard-8 (8 vCPU, 32 GB) |
| Namespace | production |
| Pod CIDR | 10.48.0.0/14 |
| Service CIDR | 10.52.0.0/20 |
| Network policy | Calico |
| Ingress controller | NGINX Ingress |
| Certificate management | cert-manager (not configured) |
| Container runtime | containerd 1.6.18 |
| OS | Container-Optimized OS |

### Appendix B: JVM Container Optimization

**Recommended JVM flags for containerized workloads**:
```bash
-XX:+UseContainerSupport          # Detect cgroup limits
-XX:MaxRAMPercentage=75.0         # Use 75% of container memory for heap
-XX:InitialRAMPercentage=50.0     # Start with 50% heap
-XX:MinRAMPercentage=25.0         # Minimum heap
-XX:+ExitOnOutOfMemoryError       # Exit on OOM (let kubelet restart)
-XX:+PrintGCDetails               # GC logging
-XX:+PrintGCDateStamps            # GC timestamps
-Xloggc:/var/log/gc.log           # GC log file
-XX:+HeapDumpOnOutOfMemoryError   # Heap dump on OOM
-XX:HeapDumpPath=/var/log/heapdump.hprof
-Djava.security.egd=file:/dev/./urandom  # Faster startup
```

**Memory calculation formula for containers**:
```
Container memory limit: 4 GB (example)
JVM heap (-XX:MaxRAMPercentage=75.0): 3 GB
Non-heap (metaspace, threads, code cache): ~800 MB
Headroom for OS, other processes: ~200 MB
Total: 4 GB
```

### Appendix C: Probe Configuration Standards

| Probe Type | Purpose | Min initialDelaySeconds | Period | Threshold | Notes |
|-----------|---------|------------------------|--------|-----------|-------|
| startupProbe | Allow slow startup | 5 | 5 | 12 (60s) | JVM needs 45s |
| livenessProbe | Detect deadlock | 60 | 15 | 3 | After startup |
| readinessProbe | Traffic routing | 30 | 10 | 3 | After startup |

### Appendix D: Canary Deployment Analysis Templates

**Success rate analysis**:
```yaml
metrics:
  - name: success-rate
    successCondition: result > 99.5
    provider:
      prometheus:
        query: |
          sum(rate(http_requests_total{namespace="production",app="order-processor",status=~"2.*"}[5m]))
          / sum(rate(http_requests_total{namespace="production",app="order-processor"}[5m]))
          * 100
```

**Memory analysis**:
```yaml
metrics:
  - name: memory-usage
    successCondition: result < 80
    provider:
      prometheus:
        query: |
          max(container_memory_working_set_bytes{namespace="production",container="order-processor"})
          / max(kube_pod_container_resource_limits{resource="memory",namespace="production",container="order-processor"})
          * 100
```

### Appendix E: OPA Gatekeeper Constraint Template

```yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredprobes
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredProbes
      validation:
        openAPIV3Schema:
          properties:
            probes:
              type: array
              items:
                type: object
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredprobes
        violation[{"msg": msg}] {
          container := input.review.object.spec.template.spec.containers[_]
          not container.startupProbe
          msg := sprintf("Container %v must have a startupProbe", [container.name])
        }
```

### Appendix F: Resource Profiling CI Integration

```yaml
# .github/workflows/resource-profile.yml
name: Resource Profiling
on:
  pull_request:
    paths:
      - 'src/main/**/*.java'
jobs:
  profile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
      - name: Build with Maven
        run: mvn package -DskipTests
      - name: Start application
        run: |
          java -XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0 \
            -jar target/order-processor-*.jar &
          APP_PID=$!
          sleep 30
      - name: Measure memory
        run: |
          ps -o rss,vsz,pcpu -p $APP_PID --no-headers
          HEAP_USAGE=$(jcmd $APP_PID GC.heap_info | grep "used" | awk '{print $2}')
          echo "Heap used: $HEAP_USAGE"
      - name: Check against limits
        run: |
          RSS=$(ps -o rss --no-headers -p $APP_PID | awk '{print $1}')
          LIMIT_KB=$((4 * 1024 * 1024))  # 4 GB limit
          if [ "$RSS" -gt "$LIMIT_KB" ]; then
            echo "ERROR: Memory $RSS KB exceeds limit $LIMIT_KB KB"
            exit 1
          fi
      - name: Cleanup
        run: kill $APP_PID 2>/dev/null || true
