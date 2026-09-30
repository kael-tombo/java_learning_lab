# ANTI-PATTERNS: CI/CD & Release Engineering
## Lab 13 | Production Engineering Academy

---

## Anti-Pattern 1: Running Database Migrations on Application Pod Boot

### The Mistake
Enabling `spring.liquibase.enabled: true` or `spring.flyway.enabled: true` inside standard application container pods.

### Why It Fails
1. When Kubernetes scales a deployment from 5 to 50 pods during a release, 50 pods attempt to acquire the migration lock simultaneously.
2. If a migration is slow, lock timeouts occur, causing pods to enter `CrashLoopBackOff`.
3. Application pods require excessive DDL permissions (`ALTER TABLE`, `DROP COLUMN`) rather than read/write DML permissions, violating least privilege security.

### The Correct Production Fix
Run database migrations as a dedicated **pre-sync Kubernetes Job** (e.g. ArgoCD PreSync hook) using a restricted migration service account before the application pods are updated.

---

## Anti-Pattern 2: The "Big Bang" Friday Afternoon Production Deploy

### The Mistake
Accumulating 3 weeks of features across 12 teams into a single monolithic release and deploying to production on Friday afternoon.

### Why It Fails
- Blast radius is enormous: dozens of independent failure domains are introduced simultaneously.
- Root cause attribution is nearly impossible.
- Weekend support staffing is reduced, leading to prolonged customer outages.

### The Correct Production Fix
Ship small, decoupled, single-feature releases multiple times per day using feature flags and automated canaries.
