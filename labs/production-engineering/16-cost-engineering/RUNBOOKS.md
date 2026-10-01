# RUNBOOKS: FinOps Triage, Cloud Cost Spikes & Resource Optimization
## Lab 16 | Production Engineering Academy — Top 0.0001% Engineering

---

## Runbook 01: Triaging a Cloud Cost Anomaly Spike (AWS / GCP / Kubecost)

### 1. Severity & Trigger Conditions
- **Severity**: FinOps P1 / P2
- **Trigger**: AWS Cost Anomaly Detection or Kubecost reports $> 25\%$ day-over-day spend increase in a specific Kubernetes cluster or namespace.

### 2. Immediate Diagnostic Workflow

#### Step 1: Isolate the Spend Dimension via Kubecost CLI
```bash
# Query Kubecost cost allocation for the past 48 hours grouped by namespace
kubectl cost --service-port 9090 --service-name kubecost-cost-analyzer \
  namespace --window 2d --show-efficiency
```
**Dimension Isolation Matrix**:
- **Compute (EC2 / GCE)**: Check if pod replica count spiked or node pool autoscaled out due to an unconstrained HPA.
- **Network (Cross-AZ / NAT Gateway)**: Check if data transfer egress spiked due to disabled topology routing or uncompressed event topics.
- **Storage (EBS / Persistent Volumes)**: Check for unpruned EBS snapshots, volume expansion, or continuous heap dumps written to persistent disks.

#### Step 2: Identify Top Offending Deployments
```bash
# Identify top 10 costliest workloads in the offending namespace
kubectl cost --service-port 9090 --service-name kubecost-cost-analyzer \
  deployment -n production --window 24h
```

#### Step 3: Check for Runaway Horizontal Pod Autoscaler (HPA)
```bash
kubectl get hpa -A --sort-by='.status.currentReplicas' | tail -n 20
```
If an HPA scaled to its `maxReplicas` limit due to a low CPU target threshold (e.g. 40% CPU target):
1. Verify if the pods are actually doing work or stalling on external dependencies.
2. Temporarily cap HPA max replicas if the downstream service is degraded:
   ```bash
   kubectl patch hpa payment-service -n production --patch '{"spec":{"maxReplicas":30}}'
   ```

---

## Runbook 02: Auditing and Eliminating Stranded Kubernetes Node Capacity

### 1. Context: What is Stranded Capacity?
When pods have mismatched CPU-to-Memory ratios (e.g. 1 core : 16 GiB RAM), one resource is exhausted while the other sits idle. The Kubernetes scheduler cannot schedule new pods on the node, forcing cluster autoscalers to provision expensive new nodes.

### 2. Audit Execution

#### Step 1: Detect Cluster Resource Fragmentation
Run the following node allocation audit script:
```bash
kubectl get nodes -o custom-columns=\
NAME:.metadata.name,\
CPU_ALLOC:.status.allocatable.cpu,\
CPU_REQ:.status.allocatable.cpu,\
MEM_ALLOC:.status.allocatable.memory \
--no-headers
```
Or use `kubectl describe nodes` to view the **Non-terminated Pods Allocation**:
```bash
kubectl describe nodes | grep -A 8 "Allocated resources:"
```
*Indicator of Stranded Capacity*:
```text
Resource           Requests    Limits
cpu                1850m (92%) 4000m
memory             3200Mi (20%) 8000Mi  <--- 80% RAM WASTED / STRANDED!
```
Here, 92% of CPU is requested, preventing any further pods from scheduling, while **80% of RAM sits completely unallocatable**!

#### Step 2: Remediate Stranded Pods
1. Identify the pods scheduled on the fragmented node:
   ```bash
   kubectl get pods --all-namespaces --field-selector spec.nodeName=<NODE_NAME> -o wide
   ```
2. Realignment: Update the pod's `resources.requests` in Helm values to follow the standard $1:4$ ratio (`500m CPU / 2Gi RAM` or `1000m CPU / 4Gi RAM`).

---

## Runbook 03: Diagnosing and Eliminating Linux CFS CPU Quota Throttling

### 1. Symptoms
- Application P99 response time spikes erratically (50–150ms stalls).
- Average CPU utilization is well below 50%.
- Kubernetes pod has `resources.limits.cpu` configured.

### 2. Live Diagnostics

#### Step 1: Inspect Container Throttling Metrics
Access the Linux cgroup metrics directly from inside or outside the container:
```bash
# For cgroups v1:
cat /sys/fs/cgroup/cpu/cpu.stat
# For cgroups v2:
cat /sys/fs/cgroup/cpu.stat
```
*Output Analysis*:
```text
usage_usec 4829104820
nr_periods 128400
nr_throttled 42100        <--- 32.7% of ALL execution periods throttled!
throttled_usec 982049000  <--- 982 seconds spent frozen in kernel state!
```
If `nr_throttled / nr_periods > 0.05` ($> 5\%$), the application is suffering severe CFS quota throttling!

#### Step 2: Remove or Expand CPU Limits
Edit the Kubernetes deployment manifest:
```yaml
resources:
  requests:
    cpu: "2000m"
    memory: "4Gi"
  limits:
    # REMOVE cpu limit or set generous headroom (e.g. "8000m")
    memory: "4Gi"
```
Apply the change:
```bash
kubectl apply -f deployment.yaml
```
*Verification*: Check `nr_throttled` in `/sys/fs/cgroup/cpu.stat` after 5 minutes — it will stop incrementing.

---

## Runbook 04: Migrating a Java Microservice from x86_64 to ARM64 Graviton/Tau

### 1. Pre-Migration Dependency Audit

#### Step 1: Detect x86-Only Native Binaries (JNI / C++)
Search your project's dependency tree for known native library traps:
```bash
mvn dependency:tree | grep -E "netty-transport-native|rocksdb|snappy|sqlite|onnx"
```

#### Step 2: Verify Multi-Platform Netty Dependencies in `pom.xml`
Ensure Netty includes the `linux-aarch_64` classifier:
```xml
<dependency>
    <groupId>io.netty</groupId>
    <artifactId>netty-transport-native-epoll</artifactId>
    <classifier>linux-aarch_64</classifier>
</dependency>
```

### 2. Multi-Arch Docker Image Build & Validation
```bash
# Set up Docker Buildx instance
docker buildx create --name multiarch-builder --use
docker buildx inspect --bootstrap

# Build and push multi-arch image
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t registry.corp.internal/services/payment-service:v2.1.0 \
  --push .
```

### 3. Progressive Kubernetes Canary Rollout to ARM64 Nodes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service-arm64-canary
spec:
  replicas: 2
  template:
    spec:
      # Target ARM64 Graviton node pool specifically
      nodeSelector:
        kubernetes.io/arch: arm64
      containers:
        - name: app
          image: registry.corp.internal/services/payment-service:v2.1.0
```
Monitor application logs, error rates, and P99 latency for 24 hours before shifting 100% of production traffic.

---

## Runbook 05: Tracing and Eliminating Cross-AZ Network Egress

### 1. Diagnosis Workflow

#### Step 1: Inspect EndpointSlice Topology Hints
Verify if Kubernetes has generated Topology Hints for the target Service:
```bash
kubectl get endpointslice -l kubernetes.io/service-name=order-processing-service -o yaml
```
*Check for Hints*:
```yaml
endpoints:
  - addresses:
      - 10.244.2.14
    conditions:
      ready: true
    hints:
      forZones:
        - name: us-east-1a   <--- Endpoint strictly assigned to us-east-1a!
    zone: us-east-1a
```
If `hints` is missing:
1. Verify the Service has annotation `service.kubernetes.io/topology-mode: Auto`.
2. Verify pods are evenly distributed across all 3 zones (maxSkew $\le 1$). If all pods sit in `us-east-1a`, Kubernetes disables topology routing to prevent overloading one zone.

#### Step 2: Verify Kafka Producer Wire Compression
Check live Kafka topic byte rate with and without compression:
```bash
kafka-run-class.sh kafka.tools.GetOffsetShell \
  --bootstrap-server localhost:9092 \
  --topic orders.v1 --time -1
```
Verify Kafka producer logs indicate `compression.type = lz4`.
