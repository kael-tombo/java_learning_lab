# Lab 07: Kubernetes for Java Architects
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 10 hours | **Level**: Expert | **Domain**: Infrastructure

---

## 🎯 Objectives

- Configure Java containers correctly for Kubernetes (heap, limits, JVM flags)
- Design Kubernetes-aware health checks (liveness vs readiness vs startup probes)
- Master resource requests and limits for Java workloads
- Implement graceful shutdown for Spring Boot in K8s
- Use HorizontalPodAutoscaler with custom metrics
- Debug CrashLoopBackOff, OOMKilled, and eviction issues
- Configure PodDisruptionBudgets for zero-downtime deployments

---

## 📖 Real-World Context

**"The OOMKilled Mystery"**: Java service set with 2GB container limit, `-Xmx1g`. Should be fine, right? But K8s keeps OOMKilling the pod. Root cause: Container JVM memory = Heap (1GB) + Metaspace (256MB) + Code Cache (256MB) + Thread stacks (200 threads × 1MB = 200MB) + Direct buffers (500MB) = **2.2GB** → K8s kills it at 2GB limit. The fix: `-Xmx1.2g` with proper direct memory limits.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | K8s resource model, JVM in containers, cgroup limits |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | OOMKilled, CrashLoopBackOff, eviction incidents |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | Deployment YAML, JVM flags, health endpoints |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Stateful vs stateless, sidecar patterns |
| [RUNBOOKS.md](./RUNBOOKS.md) | K8s pod failure investigation runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | K8s architecture questions |
| [EXERCISES.md](./EXERCISES.md) | Deploy and tune a Java service in K8s |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | K8s anti-patterns (no limits, root containers, etc.) |
| [CHECKLIST.md](./CHECKLIST.md) | K8s deployment readiness checklist |

---

## ⚙️ Production K8s Deployment Example

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: payment-service
        image: company/payment-service:1.2.3
        env:
        - name: JAVA_OPTS
          value: >
            -Xmx1200m -Xms1200m
            -XX:+UseZGC -XX:+ZGenerational
            -XX:MaxMetaspaceSize=256m
            -XX:MaxDirectMemorySize=256m
            -XX:+ExitOnOutOfMemoryError
            -Xlog:gc*:file=/var/log/gc.log:time:filecount=3,filesize=20m
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"    # = requests for predictable scheduling
            cpu: "2000m"
        livenessProbe:
          httpGet: { path: /actuator/health/liveness, port: 8080 }
          initialDelaySeconds: 60    # Spring Boot needs time to start
          periodSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet: { path: /actuator/health/readiness, port: 8080 }
          initialDelaySeconds: 30
          periodSeconds: 5
        lifecycle:
          preStop:
            exec:
              command: ["sh", "-c", "sleep 5"]  # Wait for LB to drain
```

---

## 🔗 Related Labs
- Lab 13: [CI/CD & Release Engineering](../13-cicd-release-engineering/)
- Lab 16: [Cost Engineering](../16-cost-engineering/)
- Lab 20: [Production Readiness](../20-production-readiness/)
