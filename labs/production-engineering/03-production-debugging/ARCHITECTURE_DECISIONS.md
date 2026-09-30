# ARCHITECTURE DECISIONS: Production Diagnostics & Continuous Profiling
## Lab 03 | Production Engineering Academy — Top 0.0001% Engineering

---

## ADR-01: Continuous Production Profiling Architecture (Pyroscope / JFR vs Ad-Hoc async-profiler)

### Status: ACCEPTED
**Context & Problem Statement**:
Engineering teams require high-fidelity visibility into CPU hotspots, lock contention, allocation bottlenecks, and I/O wait times across 450+ production microservices. Traditional ad-hoc profiling (attaching profilers during an outage via SSH or `kubectl exec`) violates enterprise zero-trust security and provides zero historical context for intermittent anomalies that occurred hours or days earlier.

### Decision
1. **Deploy Continuous In-Process Profiling Fleet-Wide**:
   - Integrate the **Pyroscope Java agent / OpenTelemetry Continuous Profiling** across all JVM deployments.
   - Profile sampling rate: 20 Hz (20 samples per second) using `AsyncGetCallTrace` and `perf_events`.
   - Overhead constraint: Strictly bounded to $< 1.5\%$ CPU overhead and $< 40\text{MB}$ memory footprint.
2. **Context Correlation**:
   - Continuous profile samples are automatically tagged with active OpenTelemetry trace IDs and tenant identifiers (`MDC`), allowing engineers to jump directly from a slow distributed trace span into its corresponding thread flamegraph.
3. **Emergency Ad-Hoc Profiling**:
   - For novel, deep kernel/hardware interactions, SREs may attach `async-profiler` via ephemeral debug sidecar pods equipped with `CAP_SYS_PTRACE`.

### Consequences
- **Positive**:
  - Instant retrospective root cause analysis for any historical incident.
  - Safepoint-bias-free call graphs across all compiled JIT C2 methods.
- **Negative / Trade-offs**:
  - Requires maintaining a centralized profiling storage cluster (Pyroscope/Grafana Phobos backend).

---

## ADR-02: OOM Crash Forensics & Failure Policy

### Status: ACCEPTED
**Context & Problem Statement**:
When a JVM throws `OutOfMemoryError`, default behavior often leaves the JVM process alive in a zombie state: threads holding locks die, socket listeners freeze, health checks fail, but the container remains running, preventing Kubernetes from restarting the pod. Furthermore, dumping 16GB heaps to local container disk frequently causes pod evictions due to ephemeral storage exhaustion.

### Decision
1. **Fail-Fast Termination Policy**:
   - Configure all JVM production workloads with:
     ```conf
     -XX:+ExitOnOutOfMemoryError
     -XX:+HeapDumpOnOutOfMemoryError
     -XX:HeapDumpPath=/dumps/heap-%p-%t.hprof
     ```
   - Rationale: A JVM encountering an OOM is fundamentally compromised. It must terminate immediately so Kubernetes restarts a healthy replacement pod.
2. **Storage Volume Architecture**:
   - Heap dumps are written strictly to dedicated high-speed persistent volume mounts (`emptyDir` with `sizeLimit: 35Gi` or mounted Cloud Storage FUSE).
   - Dumps to container root `/tmp` are strictly blocked via deployment admission controllers.
3. **Automated Dump Upload**:
   - A Kubernetes `postStop` hook or sidecar container monitors `/dumps/`, compresses newly created `.hprof` files with `zstd -1`, and uploads them to a forensic cloud bucket before pod destruction.

### Consequences
- **Positive**:
  - Zero zombie pods starving upstream traffic during OOM events.
  - Guaranteed capture of uncorrupted heap dumps for post-incident root cause forensics.
- **Negative / Trade-offs**:
  - Requires provisioning sufficient storage headroom across Kubernetes worker nodes.

---

## ADR-03: Production Diagnostics Security & Access Model

### Status: ACCEPTED
**Context & Problem Statement**:
Exposing diagnostic tools (JDWP remote debuggers, unauthenticated Spring Boot Actuators, interactive SSH shells) introduces critical security vulnerabilities, including remote code execution and unauthorized data extraction. Conversely, stripping all diagnostic capabilities forces blind restarts during catastrophic outages.

### Decision
1. **Interactive Debugger Ban**:
   - JDWP (`-agentlib:jdwp`) is strictly prohibited in staging, canary, and production environments.
2. **Actuator Endpoint Network Isolation**:
   - Management endpoints (`/actuator/**`) run on an isolated management port (e.g. `8081`), not exposed to public ingress.
   - Access to `/actuator/threaddump`, `/actuator/loggers`, and `/actuator/heapdump` requires internal mTLS authentication and role-based access control (RBAC).
   - `/actuator/heapdump` is disabled on public APIs to prevent memory dump exfiltration containing sensitive tokens.
3. **Zero-Trust Ephemeral Debugging**:
   - In-depth diagnostics (`jcmd`, `jstack`, `bpftrace`) are executed via Kubernetes Ephemeral Debug Containers (`kubectl debug pod/... --image=eclipse-temurin:21-jdk`), avoiding permanent bloated tools in runtime production images.

### Consequences
- **Positive**:
  - Eliminates unauthenticated RCE attack vectors while preserving surgical forensic capabilities.
- **Negative / Trade-offs**:
  - Diagnostic access requires explicit IAM permissions and audit-logged jumpbox execution.

---

## ADR-04: Off-Heap & Native Memory Observability Architecture

### Status: ACCEPTED
**Context & Problem Statement**:
High-throughput microservices using Netty, gRPC, and Kafka frequently allocate off-heap memory (`DirectByteBuffer`, native socket buffers, Metaspace, JNI). Standard APM agents and heap dumps only inspect the garbage-collected heap, leaving off-heap memory leaks invisible until pods are unexpectedly OOMKilled by the OS kernel.

### Decision
1. **Mandatory Native Memory Tracking (NMT)**:
   - Enable `-XX:NativeMemoryTracking=summary` on all production microservices.
   - Track native memory categories: `Java Heap`, `Class (Metaspace)`, `Thread Stacks`, `Code (JIT)`, `GC`, `Arena Chunk`, and `Internal`.
2. **Netty Leak Detection Standard**:
   - Set `-Dio.netty.leakDetection.level=PARANOID` on canary environments and `ADVANCED` on production staging.
   - Alert on `ResourceLeakDetector` error logs in Datadog/Splunk.
3. **Kernel-Level eBPF Diagnostics**:
   - Maintain `memleak` eBPF scripts on Kubernetes worker nodes to track C-level `malloc()` and `free()` mismatches for JNI libraries (e.g., RocksDB, Zstandard).

### Consequences
- **Positive**:
  - Complete visibility into native memory growth before container RSS limits are breached.
- **Negative / Trade-offs**:
  - NMT imposes ~1% memory overhead for tracking metadata tables.
