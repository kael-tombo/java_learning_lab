# PRODUCTION SCENARIOS: Cost Engineering & FinOps
## Lab 16 | Production Engineering Academy

---

## Scenario 1: The $45,000/Month Cross-Availability Zone Data Egress Shock

### Context
A fintech platform running on AWS EKS across 3 Availability Zones (`us-east-1a`, `us-east-1b`, `us-east-1c`) with 60 microservices communicating via Kafka and gRPC.

### The Disaster
The monthly AWS bill arrived with a **$45,000 charge under "Inter-AZ Data Transfer"** (billed at $0.01 per GB in each direction = $0.02/GB total):
- Kubernetes services were routing requests randomly across pods in all 3 AZs.
- Pods in `us-east-1a` were calling pods in `us-east-1b`, which wrote to Kafka brokers in `us-east-1c`.
- Over 2.2 Petabytes of uncompressed JSON and intra-service traffic crossed AZ boundaries every month!

### The Architectural Fix
1. Enabled **Kubernetes Topology Aware Routing** (`service.kubernetes.io/topology-mode: Auto`):
   Directs traffic to endpoints within the same Availability Zone whenever available, eliminating 85% of cross-AZ traffic.
2. Enabled Snappy / zstd compression on all Kafka topics and gRPC payloads.
3. Monthly AWS data transfer bill plummeted from **$45,000 to $4,200** (90.6% cost reduction).

---

## Scenario 2: Over-Provisioned Heap & Stranded Kubernetes Capacity

### Context
A fleet of 80 microservices each configured with `resources.requests.memory: 16Gi` by default.

### The Discovery
- Prometheus metrics revealed that 90% of the microservices had actual heap utilization of $< 1.8\text{ GB}$.
- 14.2 GB of memory per pod was completely idle, yet Kubernetes reserved the full 16 GiB on EC2 worker nodes.
- The company was paying for 120 expensive `m6i.4xlarge` EC2 instances ($38,000/month) to host empty reserved memory!

### The Fix
Implemented **Vertical Pod Autoscaler (VPA)** in recommendation mode to right-size pods to `2Gi requests / 4Gi limits` and enabled G1GC / ZGC periodic heap uncommit (`-XX:ZUncommit=true`).
Fleet shrunk from 120 nodes to 28 nodes, saving **$29,000 every month**.
