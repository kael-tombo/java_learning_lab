# CHECKLIST: Production Diagnostics Readiness
## Lab 03 | Production Engineering Academy

---

## 1. JVM Diagnostics Configuration Checklist
- [ ] `-XX:+HeapDumpOnOutOfMemoryError` configured.
- [ ] `-XX:HeapDumpPath` points to mounted, persistent volume with $\ge 1.5\times$ `-Xmx` available space.
- [ ] `-XX:+ExitOnOutOfMemoryError` or `-XX:+CrashOnOutOfMemoryError` configured so failing pods are promptly terminated and restarted by Kubernetes.
- [ ] JFR circular buffer enabled (`-XX:StartFlightRecording=disk=true,maxsize=256m,maxage=10m`).
- [ ] Garbage collection unified logging configured:
  `-Xlog:gc*,gc+phases=debug:file=/var/log/jvm/gc-%t.log:time,uptime,pid:filecount=5,filesize=50m`
- [ ] Thread stack size appropriately budgeted (`-Xss1m` or `-Xss512k`).

## 2. Dynamic Observability & Actuator Gates
- [ ] Dynamic log level modification enabled (`/actuator/loggers`) and restricted to authenticated internal traffic.
- [ ] Thread dump endpoint (`/actuator/threaddump`) functional and responsive under load.
- [ ] Ingress/API Gateway blocks external access to diagnostic endpoints.

## 3. Tooling & Incident Verification
- [ ] `jcmd` available in container base image (use `eclipse-temurin:21-jre` or standard JDK base rather than minimal distroless that strips debugging utilities, or maintain an ephemeral debug container with tools).
- [ ] Diagnostic runbooks tested in staging environment.
- [ ] Automated alerts trigger when JVM process spends $> 10\%$ CPU time in Garbage Collection.
