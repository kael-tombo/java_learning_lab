# RUNBOOKS: Kubernetes & Containerized Java Production Triage
## Lab 07 | Production Engineering Academy — Top 0.0001% Engineering

---

## Runbook 01: Diagnosing and Remediating Container Exit Code 137 (Linux OOM-Killer)

### 1. Severity & Symptoms
- **Severity**: P1 (Service Unavailable) or P2 (Degraded Replicas)
- **Symptom**: Pod status shows `OOMKilled: true`, `Last State: Terminated with Exit Code: 137`.
- **Mystery**: No `OutOfMemoryError` in application logs, no heap dump generated.

### 2. Immediate Diagnostic Workflow

#### Step 1: Verify Kernel OOM Event in Node dmesg
Retrieve the exact Linux kernel OOM killer log from the worker node:
```bash
# Identify the node hosting the killed pod
NODE_NAME=$(kubectl get pod <POD_NAME> -o jsonpath='{.spec.nodeName}')

# Check kernel logs on the host node
kubectl debug node/"$NODE_NAME" -it --image=busybox -- \
  chroot /host dmesg -T | grep -E -i "oom[-_]killer|killed process" | tail -n 25
```
*Sample Kernel Log*:
```text
[Fri Oct  1 10:14:22 2026] Memory cgroup out of memory: Killed process 48219 (java) 
total-vm:7821048kB, anon-rss:4194304kB, file-rss:12800kB, shmem-rss:0kB, 
oom_score_adj:998
```
This confirms the **Linux kernel** terminated the JVM process because anonymous RSS memory hit the container cgroup boundary.

#### Step 2: Calculate Non-Heap vs. Heap Footprint
Inspect the current deployment manifest:
```bash
kubectl get deployment <DEPLOYMENT_NAME> -o jsonpath='{.spec.template.spec.containers[0].resources}'
```
Compare `resources.limits.memory` with configured JVM flags:
- If container limit is `4Gi` and `-Xmx` is `4g`, the heap alone equals the container boundary.
- Any non-heap allocation (Metaspace, thread stacks, Netty direct memory) causes immediate termination!

#### Step 3: Immediate Mitigation
Patch the deployment to enforce percentage-based sizing with a $25\%$ safety buffer:
```bash
kubectl set env deployment/<DEPLOYMENT_NAME> \
  JAVA_TOOL_OPTIONS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"
```

---

## Runbook 02: Triage and Elimination of Linux CFS CPU Quota Throttling

### 1. Symptoms & Alert
- **Alert**: P99 latency spikes of $50 - 150\text{ms}$ during moderate traffic increases.
- **Metric**: Container CPU utilization appears normal (30–50%), but response times are degraded.

### 2. Live Diagnostic Execution

#### Step 1: Measure Container CFS Throttling Ratios
Execute directly inside the container or on the host:
```bash
# Locate the container cgroup
cat /sys/fs/cgroup/cpu.stat 2>/dev/null || cat /sys/fs/cgroup/cpu/cpu.stat
```
*Analyze Metrics*:
```text
nr_periods 150000
nr_throttled 54000        <--- 36% of periods throttled!
throttled_usec 1284090000 <--- 1,284 seconds spent suspended!
```
$$\text{Throttling Ratio} = \frac{54{,}000}{150{,}000} = 36.0\%$$
If throttling ratio $> 5\%$, the Linux kernel is freezing application execution.

#### Step 2: Strip CPU Limits from Manifest
Edit the Kubernetes deployment:
```yaml
resources:
  requests:
    cpu: "2000m"
    memory: "4Gi"
  limits:
    memory: "4Gi"
    # REMOVE limits.cpu to allow burst execution without CFS freezing
```
Apply and re-check `/sys/fs/cgroup/cpu.stat` after 5 minutes — `nr_throttled` will stop climbing.

---

## Runbook 03: Resolving Rolling Deployment `502 Bad Gateway` Drops

### 1. Symptoms
During every rolling release or Helm upgrade, Ingress controllers (NGINX/Envoy) log bursts of `502 Bad Gateway` or `Connection Refused` errors for 5–15 seconds.

### 2. Triage & Root Cause
1. Ingress access logs show errors targeting the IP address of terminating pods.
2. The Java application lacks a `preStop` sleep hook or graceful shutdown configuration.

### 3. Immediate Remediation

#### Step 1: Patch PreStop Sleep and Termination Grace Period
```bash
kubectl patch deployment <DEPLOYMENT_NAME> --patch '
spec:
  template:
    spec:
      terminationGracePeriodSeconds: 60
      containers:
        - name: app
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 15"]
'
```

#### Step 2: Enable Spring Boot Graceful Shutdown
Verify or set Spring environment variable:
```bash
kubectl set env deployment/<DEPLOYMENT_NAME> \
  SERVER_SHUTDOWN=graceful \
  SPRING_LIFECYCLE_TIMEOUT_PER_SHUTDOWN_PHASE=30s
```
*Verification*: Perform a rolling restart (`kubectl rollout restart deployment/<DEPLOYMENT_NAME>`) while running an HTTP load generator (`wrk` or `hey`). Verify $0$ non-2xx responses.

---

## Runbook 04: Troubleshooting CoreDNS Saturation & 5-Second DNS Timeouts

### 1. Symptoms
- Java HTTP clients throw `java.net.UnknownHostException` or `SocketTimeoutException` taking exactly **5,000ms**.
- CoreDNS pods report high CPU usage ($> 90\%$) and UDP packet drops.

### 2. Live Diagnostics

#### Step 1: Check CoreDNS Metrics & Packet Drops
```bash
kubectl top pods -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50 | grep -E "timeout|drop"
```

#### Step 2: Verify `ndots:5` Resolution Explosion
Inspect `/etc/resolv.conf` inside the application pod:
```bash
kubectl exec <POD_NAME> -- cat /etc/resolv.conf
```
If `options ndots:5` is present and the application queries short names or external domains without trailing dots (e.g. `api.twilio.com`), every lookup generates up to 5 UDP queries.

#### Step 3: Remediate via Pod `dnsConfig`
Patch deployment with optimized `ndots` or use NodeLocal DNSCache:
```yaml
spec:
  template:
    spec:
      dnsConfig:
        options:
          - name: ndots
            value: "2"
```

---

## Runbook 05: Debugging Pod CrashLoopBackOff Caused by Coupled Liveness Probes

### 1. Symptoms
A fleet of 40 pods is trapped in `CrashLoopBackOff`. As soon as a pod starts, it is killed after 60 seconds.

### 2. Diagnosis Workflow

#### Step 1: Inspect Pod Termination Reason
```bash
kubectl describe pod <POD_NAME> | grep -A 5 "Last State:"
kubectl describe pod <POD_NAME> | grep -A 3 "Liveness:"
```
*Look for*:
```text
Warning  Unhealthy  10s  kubelet  Liveness probe failed: HTTP probe failed with statuscode: 503
Normal   Killing    10s  kubelet  Container app failed liveness probe, will be restarted
```

#### Step 2: Inspect Liveness Endpoint Output
Port-forward directly to a starting pod and curl the probe endpoint:
```bash
kubectl port-forward <POD_NAME> 8080:8080 &
curl -i http://localhost:8080/actuator/health
```
If response is:
```json
{"status":"DOWN","components":{"db":{"status":"DOWN","details":{"error":"Connection refused"}}}}
```
The liveness probe is inspecting external database health!

#### Step 3: Decouple Liveness from External Dependencies
Immediately update the liveness probe path to `/actuator/health/liveness`:
```bash
kubectl patch deployment <DEPLOYMENT_NAME> --patch '
spec:
  template:
    spec:
      containers:
        - name: app
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
'
```
This halts the restart storm and allows pods to stay running while the database recovers.
