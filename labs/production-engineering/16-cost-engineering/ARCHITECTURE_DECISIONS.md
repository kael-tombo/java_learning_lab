# ARCHITECTURE DECISIONS: Enterprise Cost Engineering Standards
## Lab 16 | Production Engineering Academy

---

## ADR-01: ARM64 Graviton Migration & Multi-AZ Cost Optimization

### Status: ACCEPTED

### Context
Annual cloud compute and cross-AZ networking spend reached $1.8M across 400 microservices on x86 EC2 instances.

### Decisions
1. **Mandatory ARM64 Graviton Migration**:
   - All containerized Java workloads must build multi-arch images (`linux/amd64` and `linux/arm64`) using Docker Buildx.
   - Kubernetes node pools migrate from `m6i` (Intel) to `m7g` (Graviton 3/4).
2. **Topology-Aware Routing Standard**:
   - Enable `service.kubernetes.io/topology-mode: Auto` on all internal Kubernetes services.
   - Restrict cross-AZ network calls to failover scenarios only.
3. **Continuous Rightsizing Policy**:
   - Vertical Pod Autoscaler (VPA) runs in recommendation mode on all staging and production namespaces.
   - Memory requests must reflect p95 actual usage + 25% safety margin.

### Consequences
- Decreased annual cloud infrastructure spend by 38% ($680,000 annual savings).
- Maintained equal or better p99 latency SLAs.
