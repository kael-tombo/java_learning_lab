# ARCHITECTURE DECISIONS: Production Diagnostics & Continuous Profiling
## Lab 03 | Production Engineering Academy

---

## ADR-01: Continuous Production Profiling Architecture (eBPF vs JFR vs async-profiler)

### Status: ACCEPTED

### Context
Engineering teams need observability into CPU hotspots, lock contention, off-heap allocations, and I/O wait times across 450+ production microservices without incurring significant runtime overhead or risking service availability.

### Decision Drivers
1. **Low Runtime Overhead**: Profiling must impose $< 2\%$ CPU overhead and $< 50\text{ MB}$ memory footprint.
2. **Safepoint Independence**: Avoid safepoint bias to capture accurate stack traces in JIT-compiled loops.
3. **Container Compatibility**: Seamless operation inside Kubernetes (unprivileged or minimal capabilities).
4. **Historical Forensics**: Ability to analyze what occurred during an incident 3 days ago.

### Evaluated Options
- **Option 1: Periodic ad-hoc async-profiler CLI**: Executed via SSH or `kubectl exec`.
  - *Cons*: Cannot diagnose retrospective incidents; requires cluster admin shell access; violates zero-trust security.
- **Option 2: Continuous JFR with Prometheus/Grafana or Pyroscope / Parca**:
  - Continuous low-frequency sampling (10-20 Hz) streaming directly to centralized profiling backend.
  - *Pros*: Complete historical flamegraphs; 0.5-1% CPU overhead; zero security vulnerability; correlates seamlessly with traces (OpenTelemetry span IDs).

### Decision
Standardize on continuous profiling via **Pyroscope Java agent / JFR integration**:
- Default configuration: 20 Hz CPU sampling, lock profiling enabled for delays $> 10\text{ms}$.
- Direct integration with OpenTelemetry traces: Every profile sample carries active trace and span IDs.

---

# CHECKLIST: Production Diagnostics Readiness

### Diagnostic Preparedness
- [ ] JVM startup flags include:
  - `-XX:+HeapDumpOnOutOfMemoryError`
  - `-XX:HeapDumpPath=/dumps/heap-%p.hprof`
  - `-XX:+ExitOnOutOfMemoryError`
- [ ] Ephemeral scratch volume mounted with sufficient capacity (at least $1.5\times$ max heap).
- [ ] JFR continuous circular recording enabled in production startup script:
  `-XX:StartFlightRecording=disk=true,maxsize=256m,maxage=10m,dumponexit=true,path=/dumps/exit.jfr`
- [ ] Spring Boot Actuator endpoints secured with mTLS or internal token:
  - `/actuator/threaddump` enabled
  - `/actuator/heapdump` disabled on public ingress
  - `/actuator/loggers` enabled for runtime dynamic log adjustments.
- [ ] Linux capabilities configured: `SYS_PTRACE` permitted in staging for deep eBPF/async-profiler troubleshooting.
