# PRODUCTION SCENARIOS: Release Engineering Incidents
## Lab 13 | Production Engineering Academy

---

## Scenario 1: The Rolling Update Schema Incompatibility Catastrophe

### Context
A fintech customer profile service running 40 pods. An engineer needed to rename column `phone_number` to `contact_number`. The PR included a Liquibase migration dropping `phone_number` and adding `contact_number`, alongside code changes reading `contact_number`.

### The Disaster
- Kubernetes initiated a standard rolling deployment: 5 pods updated to v2, 35 pods remained on v1.
- Liquibase executed immediately upon v2 startup, executing:
  `ALTER TABLE users DROP COLUMN phone_number;`
- The 35 active pods still running v1 immediately threw `PSQLException: Column "phone_number" does not exist`!
- Every single customer login and registration request routed to the 35 v1 pods failed with HTTP 500.
- When the on-call engineer attempted to roll back the deployment to v1, the rolled-back v1 pods also crashed on startup because the database column was already gone!
- Mean Time to Recovery (MTTR): 3.5 hours. Database had to be restored from point-in-time snapshot.

### The Lesson
Database migrations must **always** be backward-compatible with the currently running version of code. Never drop a column in the same deployment that ceases using it.

---

## Scenario 2: The Feature Flag Cascading Storm

### Context
A new recommendation engine was guarded behind a dynamic feature flag in LaunchDarkly.

### The Failure Mode
- At 10:00 AM, product management toggled the feature flag to `true` for 100% of global users.
- The new recommendation engine made 12 external database queries per page load instead of 1.
- Global database CPU spiked to 100% within 15 seconds.
- When engineers panicked and toggled the feature flag back to `false`, the feature flag client had a reconnection retry bug that overwhelmed the internal network with socket reconnects, keeping the services unresponsive for 25 minutes.

### The Architectural Standard
Never flip feature flags from 0% to 100% instantaneously. Follow staged progressive rollouts (1% -> 5% -> 25% -> 100%) with automated health kill-switches.
