# CHECKLIST: Production Release Readiness
## Lab 13 | Production Engineering Academy

---

## 1. Pre-Deployment Verification
- [ ] Database migrations backward-compatible with currently running version.
- [ ] Database indexes created concurrently (`CREATE INDEX CONCURRENTLY`).
- [ ] Docker image digest (SHA256) used in deployment manifest instead of mutable `latest` tag.
- [ ] Feature flags configured with default safe fallback state.

## 2. Progressive Delivery & Rollout Gates
- [ ] Canary rollout configured with automated analysis template.
- [ ] Error rate and latency thresholds verified against current production baseline.
- [ ] Rollback runbook tested and verified.

## 3. Post-Deployment Verification
- [ ] Automated health checks passing on canary pods.
- [ ] Prometheus error budget burn rate remains flat during step increments.
- [ ] No spike in unhandled exceptions in Sentry/Datadog.
