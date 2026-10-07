# Prevention: Kubernetes Pod CrashLoop

## Strategic Prevention Framework

This document outlines a comprehensive prevention strategy based on Google SRE principles (Chapter 6 — Monitoring, Chapter 15 — Postmortem Culture), Netflix Tech Blog on container resource tuning, and Kubernetes SIG recommendations.

## Layer 1: Startup Probe Mandate

### Standard Probe Template

```yaml
# Base probe configuration for all JVM workloads
# Must be included in ALL Kubernetes deployments
spec:
  template:
    spec:
      containers:
        - startupProbe:
            httpGet:
              path: /actuator/health
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 5
            failureThreshold: 12  # 60 seconds max startup
          livenessProbe:
            httpGet:
              path: /actuator/health
              port: 8080
            initialDelaySeconds: 60  # After startup probe succeeds
            periodSeconds: 15
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
```

### Admission Controller Validation

```yaml
# OPA Gatekeeper constraint to enforce startup probes
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredProbes
metadata:
  name: require-startup-probe
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment", "StatefulSet"]
  parameters:
    probes:
      - type: "startupProbe"
        port: 8080
      - type: "livenessProbe"
        minInitialDelaySeconds: 30
      - type: "readinessProbe"
        minInitialDelaySeconds: 15
```

## Layer 2: Resource Rightsizing

### JVM Container Memory Calculator

```java
package com.acmecorp.infra;

public class ContainerMemoryCalculator {
    private static final long KB = 1024;
    private static final long MB = KB * 1024;

    // JVM overhead components
    private static final double JIT_COMPILER_OVERHEAD_MB = 64;
    private static final double GC_OVERHEAD_MB = 128;
    private static final double CODE_CACHE_MB = 48;
    private static final double METASPACE_BASE_MB = 32;
    private static final double METASPACE_PER_CLASS_KB = 4;
    private static final double THREAD_STACK_KB = 1024;
    private static final double DIRECT_BUFFER_OVERHEAD_MB = 32;
    private static final double SOCKET_BUFFER_OVERHEAD_MB = 16;
    private static final double SAFETY_BUFFER_MB = 128;

    public static class MemoryRecommendation {
        private final int heapMB;
        private final int nativeOverheadMB;
        private final int totalMB;
        private final int containerLimitMB;

        public MemoryRecommendation(int heapMB, int threadCount, int classCount) {
            this.heapMB = heapMB;
            this.nativeOverheadMB = (int) (JIT_COMPILER_OVERHEAD_MB + GC_OVERHEAD_MB
                + CODE_CACHE_MB + METASPACE_BASE_MB
                + (METASPACE_PER_CLASS_KB * classCount / KB)
                + (THREAD_STACK_KB * threadCount / KB)
                + DIRECT_BUFFER_OVERHEAD_MB + SOCKET_BUFFER_OVERHEAD_MB
                + SAFETY_BUFFER_MB);
            this.totalMB = heapMB + nativeOverheadMB;
            this.containerLimitMB = (int) (totalMB * 1.25); // 25% headroom
        }

        @Override
        public String toString() {
            return String.format(
                "Heap: %d MB | Native: %d MB | Total: %d MB | Container Limit: %d MB",
                heapMB, nativeOverheadMB, totalMB, containerLimitMB);
        }
    }

    public MemoryRecommendation recommend(int heapMB, int threadCount, int classCount) {
        return new MemoryRecommendation(heapMB, threadCount, classCount);
    }

    public static void main(String[] args) {
        ContainerMemoryCalculator calc = new ContainerMemoryCalculator();
        MemoryRecommendation rec = calc.recommend(2048, 200, 25000);
        System.out.println(rec);
    }
}
```

## Layer 3: CI/CD Resource Profiling Gate

```yaml
# .github/workflows/resource-profile.yml
name: Resource Profiling
on:
  pull_request:
    branches: [main]
jobs:
  resource-profile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
      - name: Build application
        run: ./mvnw package -DskipTests
      - name: Run resource profiling
        run: |
          java -Xmx2g -jar target/order-processor-*.jar &
          PID=$!
          sleep 30
          ps -o rss,vsz,pcpu -p $PID
          kill $PID
      - name: Check memory limits
        run: |
          MAX_MEM=$(ps -o rss --no-headers -p $PID | awk '{print $1}')
          if [ "$MAX_MEM" -gt 4194304 ]; then
            echo "ERROR: Memory exceeds 4GB limit"
            exit 1
          fi
```

## Layer 4: Canary Deployments

```yaml
# ArgoCD rollout configuration
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: order-processor
spec:
  replicas: 50
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app: order-processor
  template:
    metadata:
      labels:
        app: order-processor
    spec:
      containers:
        - name: order-processor
          image: gcr.io/acmecorp/order-processor:v3.2.2
  strategy:
    canary:
      steps:
        - setWeight: 10
        - pause: {duration: 2m}
        - setWeight: 25
        - pause: {duration: 5m}
        - setWeight: 50
        - pause: {duration: 5m}
        - setWeight: 75
        - pause: {duration: 5m}
        - setWeight: 100
      analysis:
        templates:
          - templateName: success-rate
        args:
          - name: service-name
            value: order-processor
```

## Layer 5: Automated Rollback Triggers

```yaml
# Prometheus alert for auto-rollback trigger
- alert: PodCrashLoopingAutoRollback
  expr: |
    rate(kube_pod_container_status_restarts_total{namespace="production"}[5m]) > 0.5
  for: 1m
  labels:
    severity: critical
    auto_rollback: "true"
  annotations:
    summary: "Auto-rollback triggered for {{ $labels.deployment }}"
    runbook: "https://runbook.acmecorp.com/auto-rollback"
```

## Layer 6: Operational Readiness

### Deployment Checklist

- [ ] Resource requests match production profiling data
- [ ] Resource limits have 25% headroom above peak usage
- [ ] startupProbe configured with 60s+ failure threshold
- [ ] livenessProbe initialDelaySeconds > startup probe max time
- [ ] Readiness probe configured with circuit breaker awareness
- [ ] Canary deployment strategy configured (min 10% initial weight)
- [ ] HPA configured with min/max replicas
- [ ] PDB configured (PodDisruptionBudget)
- [ ] Resource profiling data attached to PR
- [ ] Load test results with expected thread count

## Key Prevention Metrics

| Control | Metric | Target | Owner |
|---------|--------|--------|-------|
| Startup probe adoption | % of deployments with startupProbe | 100% | SRE |
| Canary deployments | % of production deployments with canary | 100% | CI/CD |
| Resource profiling | % of PRs with resource profile | 100% | App team |
| Probe tuning | % of probes with correct initialDelay | 100% | SRE |
| Rollback time | Time to rollback failed deployment | < 5 min | SRE |
| CPU throttling | % of containers with >25% throttling | < 1% | SRE |
| OOMKilled frequency | OOMKilled events per 1000 pod-hours | 0 | SRE |

## References

- Google SRE Book — Chapter 6: Monitoring: https://sre.google/sre-book/monitoring-distributed-systems/
- Netflix Tech Blog — Container Resource Tuning: https://netflixtechblog.com/container-resource-tuning
- Datadog — Kubernetes CrashLoopBackOff: (link removed)
- Kubernetes SIG — Resource QoS: https://kubernetes.io/docs/tasks/configure-pod-container/quality-service-pod/
- Java Memory Management in Containers: (link removed)
