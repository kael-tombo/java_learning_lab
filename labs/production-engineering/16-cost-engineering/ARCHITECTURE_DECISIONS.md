# ARCHITECTURE DECISIONS: Enterprise Cloud Cost Engineering & FinOps Standards
## Lab 16 | Production Engineering Academy — Top 0.0001% Engineering

---

## ADR-01: Fleet-Wide Migration to ARM64 (AWS Graviton 3/4 / GCP Tau T2A)

### Status: ACCEPTED

### Context
Annual cloud compute spend across the enterprise microservice fleet ($450$ containerized Java services on AWS EKS) reached $\$3.2\text{M}$ on Intel `m6i` instances. Benchmarking demonstrated that ARM64 Neoverse cores deliver dedicated physical cores (no hyperthreading SMT contention), larger L2 private caches ($2\text{MB}$ per core vs $0.5\text{MB}$ shared on x86), and a $20\%$ lower base hourly instance cost.

### Decision
1. **Mandatory Multi-Arch Container Builds**:
   - All CI/CD pipelines must compile container images for both `linux/amd64` and `linux/arm64` using Docker Buildx or Jib.
2. **Native Dependency Audit**:
   - Every JNI / C++ library dependency must explicitly bundle `aarch64` native binaries (e.g. Netty epoll, RocksDB, Snappy, LZ4).
3. **Node Pool Modernization**:
   - EKS / GKE node pools will migrate to AWS Graviton 3/4 (`m7g`, `c7g`) and GCP Tau T2A instances.

### Architectural Blueprint
```yaml
# Multi-Arch GitHub Actions CI Workflow:
- name: Build and Push Multi-Arch Image
  uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: registry.corp.internal/services/order-service:${{ github.sha }}
```

### Consequences
- **Positive**: 
  - $20\%$ immediate cost reduction on EC2 hourly compute.
  - $15\% - 25\%$ higher throughput per vCPU for compute-bound Java workloads.
  - Net cost-performance improvement: **$\approx 38\%$ reduction in annual compute spend** ($\$1.2\text{M}$ saved annually).
- **Negative / Operational**:
  - Requires maintaining multi-arch base images.
  - Legacy services using unmaintained x86-only JNI libraries must run on isolated legacy node pools.

---

## ADR-02: Mandatory Topology-Aware Routing & Wire Compression Policy

### Status: ACCEPTED

### Context
Monthly AWS billing revealed $\$54,000/\text{month}$ in "Inter-AZ Data Transfer" charges. Analysis showed that default Kubernetes `kube-proxy` round-robin was routing $66.7\%$ of internal microservice RPC calls across Availability Zones, and Kafka topics were publishing uncompressed JSON events across regions.

### Decision
1. **Kubernetes Topology-Aware Routing**:
   - All internal Kubernetes `Service` manifests must include the annotation:
     ```yaml
     service.kubernetes.io/topology-mode: Auto
     ```
   - Kube-proxy will restrict traffic strictly to endpoints residing in the same Availability Zone as the calling client, with automatic fallback during zone impairment.
2. **Mandatory Wire Compression Standards**:
   - All Kafka producers must configure `compression.type=lz4` or `snappy`.
   - All gRPC clients and servers must enable Gzip/Snappy framing for payloads $> 1\text{KB}$.

### Consequences
- Cross-AZ network traffic dropped by $88\%$ across the cluster.
- Kafka disk storage and cross-AZ replication egress reduced by $65\%$.
- Annual networking spend slashed by $\$520,000$.

---

## ADR-03: JVM Dynamic Memory Elasticity & Active Heap Uncommit

### Status: ACCEPTED

### Context
Kubernetes worker nodes were running at only $35\%$ average RAM utilization during non-peak business hours, yet Cluster Autoscaler could not scale down nodes because JVM processes maintained high physical RSS allocations (monotonic heap growth without deallocation).

### Decision
1. **Active Heap Uncommit Configuration**:
   - All containerized Java services running Generational ZGC or G1GC must enable memory uncommit to release physical pages back to the Linux kernel via `madvise(MADV_DONTNEED)`.
   - Flag standard for Generational ZGC:
     ```bash
     -XX:+UseZGC -XX:+ZGenerational -XX:+ZUncommit -XX:ZUncommitDelay=300
     ```
   - Flag standard for G1GC:
     ```bash
     -XX:+UseG1GC -XX:G1PeriodicGCInterval=60000 -XX:G1PeriodicGCSystemLoadThreshold=0.5
     ```
2. **Compressed OOPs Cap**:
   - Maximum heap allocation (`-Xmx`) must never be set between $31.5\text{ GiB}$ and $40\text{ GiB}$. Heaps must either be capped at `-Xmx31g` to maintain 32-bit Compressed OOPs, or set to $\ge 48\text{ GiB}$ if large scale is required.

### Consequences
- Off-peak RSS memory usage dropped by $60\%$, allowing Karpenter to consolidate nodes during nights and weekends.
- Avoided the 32 GB Compressed OOPs performance cliff fleet-wide.

---

## ADR-04: Kubernetes Resource Sizing & CFS Throttling Elimination

### Status: ACCEPTED

### Context
Microservices exhibited unexplained P99 latency spikes of $50 - 150\text{ms}$ during brief traffic bursts despite low average CPU usage. Investigation revealed Linux CFS quota throttling was freezing application threads whenever CPU limits were reached within a $100\text{ms}$ period. Teams reacted by over-requesting CPU cores by $300\%$, drastically inflating costs.

### Decision
1. **CPU Limit Policy**:
   - Production Java pods **must not specify CPU limits**, or must specify limits at least $4\times - 6\times$ higher than requests.
   - Resource guarantees are enforced via **CPU requests** alone for Kubernetes scheduling and bin-packing.
2. **Memory Request / Limit Equality**:
   - To guarantee predictable node scheduling and prevent overcommitted node memory crashes, **Memory Request must equal Memory Limit** (Guaranteed QoS class):
     ```yaml
     resources:
       requests:
         cpu: "1000m"
         memory: "4Gi"
       limits:
         memory: "4Gi"
         # No cpu limit to allow burst execution without CFS throttling
     ```
3. **Ratio Standardization**:
   - Standardize all pod sizes to $1:4$ CPU-to-Memory ratios (`0.5 CPU / 2Gi`, `1 CPU / 4Gi`, `2 CPU / 8Gi`, `4 CPU / 16Gi`) to match physical cloud instance types.

### Consequences
- CFS throttling latency spikes eliminated completely.
- Cluster bin-packing density improved from $62\%$ to $94\%$, eliminating $40$ worker nodes.

---

## ADR-05: Stateless Workload Execution on Spot / Preemptible Nodes

### Status: ACCEPTED

### Context
Stateless API gateways, asynchronous batch consumers, and worker pools were running exclusively on expensive On-Demand EC2 instances. Spot instances provide identical hardware at a $60\% - 85\%$ price discount.

### Decision
1. **Target Workload Qualification**:
   - All asynchronous Kafka consumer workers, batch processors, and idempotent stateless HTTP services must deploy to Spot node pools managed by Karpenter.
2. **Mandatory Spot Interruption Protocol**:
   - Pods must run the `aws-node-termination-handler` or subscribe to IMDS Spot interruption notices.
   - Java applications must implement a graceful drain hook:
     - Catch `SIGTERM`.
     - Stop receiving new incoming requests (fail readiness probe).
     - Flush in-flight database transactions and commit Kafka offsets within 60 seconds (well within the 120-second AWS Spot notice window).
3. **Diversity & Fallback**:
   - Karpenter configured with at least 8 diverse instance types across multiple generations (`c6g`, `c7g`, `m6g`, `m7g`) to prevent capacity pool exhaustion.

### Consequences
- Compute cost for batch and asynchronous processing reduced by $72\%$.
- Zero data loss during Spot node terminations due to graceful shutdown hooks.
