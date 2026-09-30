# CHECKLIST: Cost Engineering & FinOps Readiness
## Lab 16 | Production Engineering Academy

---

## 1. Compute & JVM Memory Right-Sizing
- [ ] Heap size capped at $\le 31\text{ GB}$ to retain 32-bit Compressed OOPs pointers.
- [ ] Memory requests aligned with measured p95 usage (not arbitrary round numbers like 16Gi).
- [ ] `-XX:+ZUncommit` or G1 periodic uncommit enabled to return idle memory to OS.
- [ ] ARM64 (Graviton) compatibility verified for all container base images.

## 2. Networking & Data Egress
- [ ] Topology-Aware Routing enabled on internal Kubernetes services to eliminate cross-AZ transfer fees.
- [ ] Kafka producers configured with `compression.type=snappy` or `zstd`.
- [ ] Web APIs enforce Gzip / Brotli response compression.

## 3. FinOps & Cost Governance
- [ ] Kubecost / OpenCost deployed for pod-level cost attribution.
- [ ] Resource quotas and limits enforced per namespace.
- [ ] Automated cost anomaly alerts configured in cloud provider console.
