# PRODUCTION READINESS CHECKLIST: JVM Diagnostics & Troubleshooting
## Lab 03 | Go-Live Quality Gate | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. JVM Startup Diagnostic Flags Matrix

- [ ] **OOM Crash & Capture Policy Configured**:
  - [ ] `-XX:+HeapDumpOnOutOfMemoryError` enabled.
  - [ ] `-XX:HeapDumpPath=/dumps/heap-%p-%t.hprof` configured to a mounted persistent volume.
  - [ ] `-XX:+ExitOnOutOfMemoryError` configured to ensure failing zombie pods terminate promptly.
- [ ] **Unified JVM GC Logging Standard**:
  - [ ] Garbage collector logging enabled with rotation and timestamps:
    ```conf
    -Xlog:gc*,gc+phases=debug:file=/var/log/jvm/gc-%t.log:time,uptime,pid:filecount=5,filesize=50m
    ```
- [ ] **Native Memory Tracking (NMT) Active**:
  - [ ] `-XX:NativeMemoryTracking=summary` enabled (overhead $< 1\%$).
- [ ] **Continuous JFR Flight Recording Configured**:
  - [ ] Low-overhead circular buffer enabled on startup:
    ```conf
    -XX:StartFlightRecording=disk=true,maxsize=256m,maxage=15m,dumponexit=true,path=/dumps/exit.jfr
    ```
- [ ] **Thread Stack Sizing**:
  - [ ] `-Xss` sized explicitly (e.g. `-Xss1m` or `-Xss512k` depending on call depth).

---

## 2. Storage Volume & Ephemeral Disk Protection

- [ ] **Dedicated Scratch Volume Mounted**:
  - [ ] High-throughput volume mounted at `/dumps` with capacity $\ge 1.5\times$ `-Xmx` (e.g., minimum 30GB volume for a 16GB heap).
  - [ ] Root container `/tmp` write-locked or excluded from dump targets to prevent pod eviction by the kubelet.
- [ ] **Automated Dump Offloading / Sync**:
  - [ ] Pre-stop hook or background agent configured to compress (`zstd`) and stream `.hprof` files to Cloud Storage.

---

## 3. Dynamic Observability & Management Endpoints

- [ ] **Port Separation & Ingress Isolation**:
  - [ ] Spring Boot management port (`management.server.port=8081`) isolated from public application traffic (`server.port=8080`).
  - [ ] Public ingress controllers explicitly block all `/actuator/**` routes.
- [ ] **Dynamic Logging Configured**:
  - [ ] `/actuator/loggers` endpoint accessible internally with authenticated RBAC to permit runtime log level adjustments without restarts.
- [ ] **Heap Dump Endpoint Safety**:
  - [ ] `/actuator/heapdump` endpoint **disabled** on all environments unless protected by mTLS and strict IP whitelisting to prevent memory exfiltration.
- [ ] **Thread Dump Endpoint Operational**:
  - [ ] `/actuator/threaddump` verified functional under load without timing out.

---

## 4. Continuous Profiling & Runtime Tooling

- [ ] **Continuous Profiler Agent Deployed**:
  - [ ] Pyroscope / Parca / Datadog continuous profiling agent attached.
  - [ ] Sampling rate verified at 20 Hz (CPU) and memory allocation profiling enabled.
- [ ] **Container Diagnostic Capabilities**:
  - [ ] Base container image contains `jcmd` and debugging utilities, or the Kubernetes cluster supports `kubectl debug` with ephemeral containers (`eclipse-temurin:21-jdk`).
  - [ ] `SYS_PTRACE` capability enabled where eBPF / async-profiler tracing is required.

---

## 5. Automated Alerting & Diagnostic SLIs

| Metric / Event | Prometheus Query | Warning Threshold | Critical Page Threshold |
|---|---|---|---|
| **JVM GC Pause Overhead** | `rate(jvm_gc_pause_seconds_sum[1m]) / rate(jvm_gc_pause_seconds_count[1m])` | $> 5\%$ of CPU | $> 10\%$ of CPU |
| **Safepoint Stall Time** | `rate(jvm_safepoint_time_seconds_total[1m])` | $> 100\text{ms}/\text{sec}$ | $> 300\text{ms}/\text{sec}$ |
| **Active Thread Saturation** | `jvm_threads_live_threads / jvm_threads_peak_threads` | $> 80\%$ | $> 95\%$ |
| **Off-Heap NMT Growth** | `jvm_memory_committed_bytes{area="nonheap"}` | $> 15\% / \text{hour}$ | $> 30\% / \text{hour}$ |
| **Pod OOMKills** | `rate(kube_pod_container_status_terminated_reason{reason="OOMKilled"}[5m])` | $> 0$ | $> 0$ (Immediate Page) |
