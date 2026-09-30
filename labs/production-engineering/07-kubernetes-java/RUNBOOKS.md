# RUNBOOK: Kubernetes Java Incidents & Container Forensics
## Lab 07 | Production Engineering Academy

---

## RUNBOOK 01: Investigating OOMKilled (Exit Code 137)

**Severity**: P1 / P2  
**Symptom**: Pod restarts unexpectedly. `kubectl get pods` shows `RESTARTS: 4`, `STATUS: CrashLoopBackOff` or `OOMKilled`.

### Step 1: Confirm Container OOM Termination
```bash
kubectl describe pod <pod-name> | grep -E "Exit Code|OOMKilled|Reason"
# Look for: Last State: Terminated, Reason: OOMKilled, Exit Code: 137
```

### Step 2: Check Node Kernel Logs
```bash
kubectl get node -o wide
# On worker node:
dmesg -T | grep -i -E "oom-killer|killed process"
# Verify which process exceeded cgroup: java vs sidecar vs native memory
```

### Step 3: Check Memory Breakdown
If Exit Code 137 occurred without a JVM `OutOfMemoryError` heap dump being written:
- The Linux kernel killed the process from the outside because **Non-Heap + Heap exceeded container limit**.
- Non-heap components: Metaspace, Thread stacks ($N \times 1\text{MB}$), Netty direct byte buffers, or glibc malloc fragmentation.
- Remediation: Reduce `-XX:MaxRAMPercentage` from 85% to 70%, or raise Kubernetes container memory limit.

---

## RUNBOOK 02: CFS CPU Throttling Investigation

### Step 1: Inspect Container CPU Throttling in Prometheus
Prometheus query:
```promql
sum(rate(container_cpu_cfs_throttled_periods_total{pod=~"payment-service-.*"}[5m])) 
/ 
sum(rate(container_cpu_cfs_periods_total{pod=~"payment-service-.*"}[5m])) * 100
```
If throttling exceeds **15%**, p99 latency is actively degrading.

### Step 2: Inspect via Pod Shell
```bash
cat /sys/fs/cgroup/cpu/cpu.stat
# Look at nr_throttled and throttled_time
```

### Step 3: Mitigation
Remove or increase CPU limits in Deployment manifest:
```bash
kubectl set resources deployment payment-service --limits=cpu=4000m
```
