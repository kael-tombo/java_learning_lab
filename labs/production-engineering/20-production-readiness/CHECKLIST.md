# CHECKLIST: Production Readiness Review (PRR) Master Scorecard
## Lab 20 | Capstone | Production Engineering Academy

---

## 1. Architecture & Design Readiness
- [ ] Bounded context clearly defined (Domain-Driven Design).
- [ ] No single point of failure (SPOF); multi-AZ deployment verified.
- [ ] Stateless application containers (session state in Redis or database).
- [ ] Capacity sized to handle $3\times$ forecasted peak load.

## 2. Resilience & Failure Isolation
- [ ] Strict connection ($\le 500\text{ms}$) and read ($\le 2000\text{ms}$) timeouts on all remote calls.
- [ ] Circuit breakers (Resilience4j) wrapped around all external dependencies.
- [ ] Retries use exponential backoff with full randomized jitter; retries disabled on non-idempotent endpoints.
- [ ] Database connection pools sized using the hardware formula; `leakDetectionThreshold` enabled.
- [ ] `lifecycle.preStop.exec.command: ["/bin/sh", "-c", "sleep 15"]` configured to eliminate 502s during rolling updates.

## 3. Observability & SRE Hygiene
- [ ] OpenTelemetry distributed tracing integrated; W3C headers propagated across all hops.
- [ ] Metrics contain zero high-cardinality labels (no user IDs or UUIDs in Prometheus tags).
- [ ] Logs emitted as structured JSON with mandatory `trace_id` and `span_id`.
- [ ] Multi-window, multi-burn-rate alerts configured for critical user journeys.
- [ ] Every alerting rule contains a direct link to a verified on-call runbook (`runbook_url`).

## 4. Security & Compliance
- [ ] Zero static credentials in Git or Docker images; secrets injected from Vault / KMS.
- [ ] Container runs as non-root user (e.g. UID 10001) with read-only root filesystem.
- [ ] SSRF validation interceptor protects all outbound network calls.
- [ ] Jackson polymorphic default typing disabled; native Java serialization prohibited.

## 5. Release & Operational Preparedness
- [ ] Progressive canary rollout configured via Argo Rollouts with automated metric analysis.
- [ ] Database migrations backward-compatible (Expand-Contract pattern).
- [ ] On-call rotation established in PagerDuty with primary, secondary, and escalation manager.
- [ ] Incident Commander protocol tested in war room tabletop simulation.
- [ ] Chaos Game Day conducted verifying behavior under AZ partition and database failover.
