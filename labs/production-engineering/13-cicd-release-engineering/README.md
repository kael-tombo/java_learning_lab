# Lab 13: CI/CD Pipelines & Release Engineering
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 8 hours | **Level**: Advanced | **Domain**: DevOps / Engineering

---

## 🎯 Objectives

- Design multi-stage CI/CD pipelines for Java microservices
- Implement blue-green, canary, and rolling deployments
- Automate quality gates: tests, coverage, SAST, SCA
- Manage feature flags for safe incremental rollouts
- Implement GitOps with Argo CD or Flux
- Handle database migrations in zero-downtime deployments
- Rollback strategies and deployment runbooks

---

## 📖 Real-World Context

**"The Friday Deploy"**: Team deploys a new feature on Friday at 4 PM. Pipeline is green. Deploy to production. Monitoring shows error rate climbing to 5%. On-call scrambles, but it's a new deploy issue. Rolling back takes 8 minutes (manual kubectl). Error budget for the month consumed in 15 minutes. Post-mortem outcome: automated canary deployments with automatic rollback at 1% error rate.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | CI/CD patterns, deployment strategies, GitOps |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Bad deploys, rollback failures, database migration disasters |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | GitHub Actions, Argo CD, feature flags code |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Deployment strategy decisions |
| [RUNBOOKS.md](./RUNBOOKS.md) | Emergency rollback runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | CI/CD and release engineering questions |
| [EXERCISES.md](./EXERCISES.md) | Build a complete CI/CD pipeline |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Anti-patterns (no tests in CI, manual deploys) |
| [CHECKLIST.md](./CHECKLIST.md) | Release engineering checklist |

---

## 🔖 Zero-Downtime Database Migration Pattern

```
Step 1: Add new column (nullable, no default)       ← Both old & new code work
Step 2: Deploy new code (writes to both columns)    ← Backward compatible
Step 3: Backfill old rows                           ← Background job
Step 4: Add constraint / rename (maintenance)       ← Old code no longer deployed
Step 5: Drop old column                             ← Cleanup
```

---

## 🔗 Related Labs
- Lab 07: [Kubernetes for Java](../07-kubernetes-java/)
- Lab 14: [Incident Response](../14-incident-response/)
- Lab 20: [Production Readiness](../20-production-readiness/)
