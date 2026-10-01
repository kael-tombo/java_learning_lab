# CHECKLIST: Cloud Cost Engineering & FinOps Production Readiness
## Lab 16 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Compute & Architecture Optimization (ARM64 & Spot)

- [ ] **ARM64 Graviton / Tau Migration**:
  - [ ] Container images built as multi-arch (`linux/amd64`, `linux/arm64`) using Docker Buildx.
  - [ ] All JNI native dependencies verified to bundle `linux-aarch_64` binaries (`netty`, `rocksdb`, `snappy-java`, `lz4`).
  - [ ] EKS/GKE node pools migrated to ARM64 instances (`m7g`, `c7g`, `t2a`), capturing $20\%$ lower base compute pricing.
- [ ] **Spot & Preemptible Execution**:
  - [ ] Stateless APIs, asynchronous Kafka consumers, and batch workers configured on Spot node pools.
  - [ ] Spot node pools configured with $\ge 8$ diverse instance families across all AZs to prevent capacity pool exhaustion.
  - [ ] Java application implements graceful shutdown hook catching `SIGTERM` and completing drains within 60 seconds (well within AWS 120s Spot notice).
- [ ] **CFS Quota Throttling Elimination**:
  - [ ] Production pods do not specify strict CPU limits (`limits.cpu`) unless required by multitenancy hard isolation.
  - [ ] Verified `nr_throttled / nr_periods < 1%` in `/sys/fs/cgroup/cpu.stat` under peak traffic load.

---

## 2. JVM Memory & Sizing Economics

- [ ] **Compressed OOPs Protection**:
  - [ ] Heap size (`-Xmx`) strictly capped at $\le 31\text{ GiB}$ to maintain 32-bit Compressed OOPs (`-XX:+UseCompressedOops`).
  - [ ] Verified `UseCompressedOops = true` via `java -XX:+PrintFlagsFinal -version`.
  - [ ] Heaps between 32 GiB and 44 GiB strictly forbidden due to the reference doubling penalty.
- [ ] **Dynamic Memory Elasticity (Uncommit)**:
  - [ ] Generational ZGC configured with `-XX:+ZUncommit -XX:ZUncommitDelay=300` to return idle physical memory pages to the OS kernel.
  - [ ] G1GC configured with periodic uncommit (`-XX:G1PeriodicGCInterval=60000`) for off-peak workloads.
- [ ] **Non-Heap Headroom & Container Limits**:
  - [ ] Container memory limits sized with at least $25\%$ headroom above `-Xmx` to accommodate Metaspace, Code Cache, thread stacks, and Netty direct memory (`-XX:MaxRAMPercentage=75.0`).
  - [ ] Thread stack size audited (`-Xss256k` or `-Xss512k`) or migrated to Java 21 Virtual Threads (Project Loom) to eliminate platform thread stack bloat.

---

## 3. Network Egress & Data Transfer Optimization

- [ ] **Topology-Aware Routing**:
  - [ ] Internal Kubernetes Services annotated with `service.kubernetes.io/topology-mode: Auto`.
  - [ ] Pods evenly distributed across Availability Zones using `topologySpreadConstraints` with `maxSkew: 1`.
  - [ ] Verified via `EndpointSlice` YAML that local zone hints are populated.
- [ ] **Wire Compression Standards**:
  - [ ] Kafka producers configured with `compression.type=lz4` or `snappy`, with `batch.size=65536` and `linger.ms=10`.
  - [ ] High-throughput gRPC clients and servers enforce Gzip/Snappy compression framing.
- [ ] **Public NAT Gateway Egress Elimination**:
  - [ ] VPC Endpoints (AWS PrivateLink) deployed for S3, DynamoDB, SecretsManager, and ECR to avoid paying $\$0.045/\text{GB}$ NAT Gateway processing fees.

---

## 4. Kubernetes Node Bin-Packing & Rightsizing

- [ ] **Resource Ratio Alignment**:
  - [ ] Pod CPU and Memory requests standardized to $1:4$ ratio (`500m/2Gi`, `1000m/4Gi`, `2000m/8Gi`) matching physical cloud instance ratios.
  - [ ] Zero pods requesting extreme skewed ratios (e.g. 100m CPU with 16Gi RAM) on general-purpose node pools.
- [ ] **Continuous Rightsizing Governance**:
  - [ ] Vertical Pod Autoscaler (VPA) deployed in recommendation mode across all production namespaces.
  - [ ] Memory requests aligned to P95 actual historical usage $+ 20\%$ safety buffer.
  - [ ] Node allocation efficiency audited monthly via Kubecost ($\ge 85\%$ allocated resource efficiency target).

---

## 5. FinOps Tagging & Cost Attribution

- [ ] **Mandatory Kubernetes Metadata Labels**:
  - [ ] `finops.cost-center`: Identifies the responsible financial business unit.
  - [ ] `finops.service-tier`: Identifies business criticality (`tier-0`, `tier-1`, `tier-2`).
  - [ ] `finops.environment`: (`production`, `staging`, `dev`).
- [ ] **Automated Anomaly Alerts**:
  - [ ] Cloud Cost Anomaly Detection alerts configured to notify the on-call engineering channel within 24 hours of any $> 20\%$ spend surge.
