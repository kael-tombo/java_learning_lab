# Lab 16: Cost Engineering & Cloud Optimization
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 8 hours | **Level**: Advanced | **Domain**: Infrastructure / Finance

---

## 🎯 Objectives

- Understand cloud cost drivers for Java workloads
- Right-size JVM memory and CPU for cost efficiency
- Implement spot instance / preemptible workload strategies
- Design cost-effective data storage and transfer patterns
- Use GraalVM native images for function-as-a-service cost reduction
- Monitor and alert on cloud spend anomalies
- Build engineering culture around cost awareness

---

## 📖 Real-World Context

**"The $200,000 Default"**: A startup used default `m5.2xlarge` instances (8 vCPU, 32GB RAM) for their API services. Profiling showed average CPU usage: 5%, memory usage: 3GB out of 32GB. They were wasting 95% of compute and 90% of memory. Switching to `c6a.xlarge` (4 vCPU, 8GB) + right-sizing JVM reduced their AWS bill from $280,000/month to $45,000/month. Same performance. Engineering leadership didn't know because there was no cost monitoring.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | Cloud pricing models, TCO analysis, cost attribution |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Cost disasters and optimization wins |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | JVM sizing, GraalVM native, Spot instance patterns |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Cost vs performance tradeoffs |
| [RUNBOOKS.md](./RUNBOOKS.md) | Cost anomaly investigation runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Cloud cost engineering questions |
| [EXERCISES.md](./EXERCISES.md) | Cost optimization exercise |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Cost anti-patterns |
| [CHECKLIST.md](./CHECKLIST.md) | Cloud cost readiness checklist |

---

## 💰 Java Cloud Cost Optimization Checklist

```
JVM Sizing:
  [ ] CPU request = average CPU usage × 1.5 (not peak)
  [ ] Memory limit = Xmx + off-heap + 512MB buffer
  [ ] Use Vertical Pod Autoscaler recommendations

Instance Types:
  [ ] Compute-optimized (c-family) for CPU-bound apps
  [ ] Memory-optimized (r-family) for memory-heavy apps (Kafka, analytics)
  [ ] General purpose (m-family) for balanced workloads
  [ ] Spot/Preemptible for batch, dev/test environments

Architecture:
  [ ] Stateless services → scale to zero off-peak
  [ ] GraalVM native for Lambda/Cloud Functions (cold start, memory)
  [ ] S3/GCS for static assets instead of instance storage
  [ ] Reserved capacity for predictable baseline load
```

---

## 🔗 Related Labs
- Lab 07: [Kubernetes for Java](../07-kubernetes-java/)
- Lab 15: [Performance Engineering](../15-performance-engineering/)
