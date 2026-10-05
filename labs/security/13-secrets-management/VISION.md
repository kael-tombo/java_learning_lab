# VISION — Secrets Management: Making Rotation Routine
> Where this lab takes you: from "use environment variables" to a lifecycle where rotation is a scheduled, observed, zero-downtime event.

## The Arc
1. **Problem** — why config files, env vars, and source control leak; the blast radius of one leaked DB password.
2. **Lifecycle** — generate, store, distribute, rotate, revoke, audit, and destroy.
3. **Storage models** — static secrets vs dynamic credentials, secret engines, leases and TTLs.
4. **Consumption** — Spring `Environment`, `@Value` pitfalls, programmatic access, caching rules.
5. **Operations** — rotation cadence, break-glass, detection, and "secret zero" hygiene.

## Milestones (checkable)
- [ ] M1: build a scanner that finds hardcoded credentials in a sample repository.
- [ ] M2: explain why an env var is still a secret in a bad place (CI logs, crash dumps, child processes).
- [ ] M3: implement a secret store with leases and prove access is denied after lease expiry.
- [ ] M4: rotate a secret with no application restart, including in a running JVM.
- [ ] M5: design a rotation procedure that survives being triggered at 3 a.m. by a page.

## Core Competencies
- Static vs dynamic credentials, and choosing per-application identity over shared accounts.
- Lease/TTL semantics and why short-lived credentials shrink blast radius.
- Secret injection patterns in Spring Boot, including the caching trap.
- Auditing: who read which secret, from where, and when it was last rotated.

## Anti-Goals
- Env vars committed to `.env` files, or secrets in `application.yml` shipped in the jar.
- A single shared database user across all services.
- Rotation described as "manual, when someone remembers".

## Interview Lens
- "Your secret is in an env var. What's still wrong with that?"
- "How do you rotate a DB password across 20 services without downtime?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: audit a repo for leaked secrets, fix the findings.
- Wk2 QUIZ/FLASHCARDS to 90%+; wire Spring to a secret store with dynamic credentials.
- Wk3 MINI_PROJECT implementing a lease-based store and rotation.
- Wk4 REAL_WORLD_PROJECT: production rotation design with detection and audit.

## Done = You Can
- Run a secret-leak audit, migrate a service to dynamic credentials, and execute a
  zero-downtime rotation with a documented, rehearsed runbook.
