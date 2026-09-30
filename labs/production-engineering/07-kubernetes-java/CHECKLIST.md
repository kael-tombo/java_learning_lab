# CHECKLIST: Kubernetes Java Production Readiness
## Lab 07 | Production Engineering Academy

---

## 1. Container Sizing & Lifecycle
- [ ] Memory request equals memory limit (Guaranteed QoS class).
- [ ] `-XX:MaxRAMPercentage=70.0` configured (no hardcoded `-Xmx`).
- [ ] `preStop` hook configured with `sleep 15` to prevent 502 errors during rolling deployment.
- [ ] `terminationGracePeriodSeconds` set to at least 60 seconds.
- [ ] Container process runs as non-root user (e.g. UID 10001).
- [ ] Java process launched as PID 1 (`exec java ...`).

## 2. Health & Startup Probes
- [ ] `startupProbe` configured with generous timeout for slow bean initialization and migrations.
- [ ] `livenessProbe` points to lightweight internal probe (e.g. `/actuator/health/liveness`).
- [ ] `readinessProbe` verifies external dependencies before accepting traffic (`/actuator/health/readiness`).
- [ ] Management port separated from business traffic port (`management.server.port=8081`).

## 3. High Availability & Scheduling
- [ ] `topologySpreadConstraints` configured across Availability Zones (`zone`).
- [ ] Pod Disruption Budget (PDB) configured (`minAvailable: 50%`).
