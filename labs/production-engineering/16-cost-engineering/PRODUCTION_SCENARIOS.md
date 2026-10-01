# PRODUCTION SCENARIOS: Cloud Cost Engineering & FinOps War Stories
## Lab 16 | Production Engineering Academy — Top 0.0001% Engineering

---

## Scenario 1: The $45,000/Month Cross-Availability Zone Data Egress Shock

### 1. Incident Context & Architecture
- **Organization**: Tier-1 FinTech Payment Clearinghouse.
- **Infrastructure**: AWS EKS cluster spanning 3 Availability Zones (`us-east-1a`, `us-east-1b`, `us-east-1c`).
- **Topology**: 60 Java microservices communicating via high-throughput gRPC and Kafka (2.2 Petabytes of intra-service traffic per month).

### 2. The Disaster
The monthly AWS billing invoice arrived with an alarming **$45,000 charge under "Inter-AZ Data Transfer"** ($0.01/GB ingress + $0.01/GB egress = $0.02/GB total):
- Finance flagged an immediate P1 FinOps escalation.
- Engineers were puzzled: "All our microservices run in the same AWS region (`us-east-1`). Why are we paying tens of thousands for data transfer?"

### 3. Root Cause Analysis
Traffic flow inspection with VPC Flow Logs revealed:
1. **Random Cross-AZ Round-Robin**:
   Kubernetes standard `kube-proxy` was routing requests evenly across all pods in all 3 zones. A request initiated by a pod in `us-east-1a` had a **66.7% probability** of being routed to a pod in `us-east-1b` or `us-east-1c`.
2. **Double-Hop Egress Multiplier**:
   - Client in Zone A calls Gateway in Zone B ($0.02/GB).
   - Gateway in Zone B calls Auth Service in Zone C ($0.02/GB).
   - Auth Service writes to Kafka broker in Zone A ($0.02/GB).
   A single user transaction crossed AZ boundaries **3 separate times**, incurring 3 independent billing events!
3. **Uncompressed Payload Tax**:
   Internal gRPC services were passing verbose uncompressed JSON strings inside protobuf byte fields.

### 4. Production Remediation & Payoff
1. **Enabled Topology-Aware Routing**:
   Added `service.kubernetes.io/topology-mode: Auto` across all internal Kubernetes Services.
   - Kube-proxy endpoint slices immediately pinned traffic to local zone pods.
   - Cross-AZ traffic dropped from **66.7% to 4.1%** fleet-wide.
2. **Enabled LZ4 Wire Compression**:
   Configured `compression.type=lz4` on Kafka producers and enabled Gzip compression framing on gRPC clients. Payload sizes dropped by **68%**.
3. **Financial Outcome**:
   - Monthly Inter-AZ Data Transfer bill collapsed from **$45,000 down to $3,800** (a **91.5% cost reduction**, saving **$494,400 annually**).

---

## Scenario 2: Over-Provisioned Heap & Stranded Kubernetes Capacity

### 1. Incident Context & Architecture
- **Fleet**: 80 Spring Boot microservices deployed on AWS EKS using 120 `m6i.4xlarge` EC2 instances (16 vCPUs, 64 GiB RAM each).
- **Monthly Compute Spend**: $38,400/month.

### 2. The Discovery via Kubecost
The FinOps team deployed Kubecost and discovered a massive cluster efficiency anomaly:
- **Allocated Memory Requests**: 94% of cluster RAM was formally "reserved" by Kubernetes pods.
- **Actual Active Memory Usage (Prometheus `jvm_memory_used_bytes`)**: Average heap usage across all 80 microservices was **only 1.6 GiB**!
- Every service Helm chart had been copied from an old legacy template specifying:
  ```yaml
  resources:
    requests:
      cpu: "1000m"
      memory: "16Gi"  # 14.4 GiB of wasted, unutilized reservation per pod!
  ```
Because Kubernetes reserves the full requested memory when scheduling pods on nodes, 120 expensive EC2 instances were being paid for solely to host **empty reserved capacity** that the JVM never touched!

### 3. Production Remediation
1. **Vertical Pod Autoscaler (VPA) Recommendation Engine**:
   Ran VPA in recommendation mode over a 14-day rolling window to calculate exact P95 memory profiles.
2. **Right-Sized Deployment Tiers**:
   Re-architected pod requests to a cost-optimal $1:4$ ratio:
   ```yaml
   resources:
     requests:
       cpu: "500m"
       memory: "2Gi"
     limits:
       memory: "3Gi"
   ```
3. **Active Heap Uncommit Configuration**:
   Configured `-XX:+UseZGC -XX:+ZGenerational -XX:+ZUncommit` to allow idle pods to shrink RSS back to the Linux kernel during low-traffic windows.
4. **Financial Outcome**:
   - Worker node count contracted from **120 instances down to 28 instances**.
   - Monthly compute spend plummeted from **$38,400 to $8,960** (saving **$353,280 annually**).

---

## Scenario 3: The CFS Throttling Cost Multiplier

### 1. Incident Context & Symptom
- **Service**: `search-indexer-service` (Java 21, Netty-based).
- **The Problem**: P99 latency jumped from 12ms to 95ms under moderate load.
- **The Junior Engineer's "Fix"**:
  Believing the service was CPU-starved, the team bumped the pod's CPU request and limit from `2000m` to `8000m` (from 2 cores to 8 cores).
- **The FinOps Disaster**: The cluster required 24 additional nodes to schedule the expanded pods, adding **$14,000/month** to the cloud bill. Yet, P99 latency **did not improve at all**!

### 2. Root Cause: Linux CFS Quota Throttling
Investigation with `cat /sys/fs/cgroup/cpu/cpu.stat` revealed:
```text
nr_periods 100000
nr_throttled 48000  (48% of all 100ms periods throttled!)
```
- Netty ran 16 event loop worker threads.
- During a burst, all 16 threads woke up simultaneously. Each thread executed for just 12ms:
  $$16 \text{ threads} \times 12\text{ ms} = 192\text{ ms of CPU time}$$
- The 200ms quota was exhausted in the first 12ms of the 100ms CFS window.
- The Linux kernel **froze all 16 threads for the remaining 88ms**!
- Bumping limits to 8 cores simply allowed 16 threads to burn the quota slightly faster before being frozen again.

### 3. Production Remediation
1. Stripped `limits.cpu` completely from the manifest, keeping only `requests.cpu: "1000m"`.
2. Threads were allowed to burst into available host CPU cycles without kernel throttling.
3. *Outcome*:
   - Throttling dropped to **0%**.
   - P99 latency instantly collapsed back to **9.4ms**.
   - Pod sizing was reduced back to 1 core, terminating the 24 superfluous EC2 nodes and saving the entire **$14,000/month**.

---

## Scenario 4: The 32 GB Compressed OOPs Outage & Capacity Cliff

### 1. Incident Context
- **Service**: `risk-analytics-batch`
- **Context**: A batch calculation service frequently threw `java.lang.OutOfMemoryError: Java heap space` when processing large end-of-quarter risk calculations on `-Xmx31g`.
- **The Incident**: An on-call engineer increased the heap from `-Xmx31g` to `-Xmx32g` to give the application "1 extra GB of breathing room."
- **The Catastrophe**: Upon restart with `-Xmx32g`, the application crashed with an OOM **faster than before**, failing before even completing step 1 of the risk run!

### 2. Forensic Autopsy
Inspection with JOL (Java Object Layout) and JVM diagnostic flags:
```bash
java -Xmx32g -XX:+PrintFlagsFinal -version | grep UseCompressedOops
# Output: bool UseCompressedOops = false
```
Because `-Xmx` crossed the 32 GiB boundary:
- The JVM disabled Compressed OOPs and expanded every reference from 4 bytes to 8 bytes.
- The 300 million cached risk objects had an average of 6 reference fields each:
  $$300{,}000{,}000 \times 6 \times 4\text{ extra bytes} = 7.2\text{ GiB of additional pointer bloat!}$$
- Moving from 31 GiB to 32 GiB added 1 GiB of physical memory, but **consumed 7.2 GiB of additional pointer overhead**!
- Usable object capacity actually **shrunk by 6.2 GiB**!

### 3. Production Remediation
1. Reverted heap to `-Xmx31g` to re-enable Compressed OOPs.
2. Replaced `HashMap<Long, RiskMetric>` with primitive-backed `LongObjectHashMap` from HPPC, eliminating boxed `Long` object references entirely.
3. Heap usage dropped from 31 GiB down to 18 GiB, saving memory and eliminating the OOM crash permanently.
