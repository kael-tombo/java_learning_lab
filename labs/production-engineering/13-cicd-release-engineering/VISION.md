# VISION — Lab 13: CI/CD Pipelines & Release Engineering

> From "the pipeline is green" to "every change is deployed progressively, automatically reversed when it is wrong, and provably safe against the database."

---

## The Arc

1. **Build once, promote the artifact** — reproducibility, digest pinning, and why per-environment rebuilds destroy the guarantee.
2. **Pipelines that people trust** — stage ordering, feedback latency, caching correctness, and the cost of flakiness.
3. **Quality gates** — which checks block a merge, what thresholds are honest, and the ratchet pattern.
4. **Deployment strategies** — rolling, blue/green, canary: availability versus blast radius, and the cost of each.
5. **Progressive delivery** — pre-declared analysis, canary steps sized by statistical power, automatic rollback.
6. **Feature flags** — deploy versus release, flag types, evaluation locality, and flag debt as combinatorial state.
7. **Databases** — expand-contract, lock time, backfill throughput, and building the rollback option before you need it.
8. **Rollback as a capability** — when it exists, when it does not, and measuring time-to-rollback as an SLO.
9. **GitOps** — desired state as code, drift, secrets, digest-driven manifests, sync waves.
10. **Measuring the delivery system** — lead time, deployment frequency, change failure rate, time to restore.

---

## Why this lab exists

Most teams have a pipeline and a rollout script. What they lack is a *risk model*: how much traffic sees a bad change before anyone notices, whether they can reverse it, and what happens to the database.

The specific goal here: **you can state, for any release, its blast radius, its detection window, and its rollback time — and you can change those numbers by design.**

---

## Milestones (checkable)

- [ ] M1: Prove build reproducibility for a real service (build twice, compare digests) and pin the base image by digest.
- [ ] M2: Restructure a real pipeline to < 10 minutes of developer-blocking feedback with per-stage timing, and eliminate the flaky-test overrides.
- [ ] M3: Implement a canary with pre-declared SLO analysis (error rate + p99 + saturation) and automatic rollback, and demonstrate both promotion and automatic reversal.
- [ ] M4: Size a canary step from the sample-size requirement, and show a too-short step failing to detect a real regression.
- [ ] M5: Run a full expand-contract migration on a real schema (add → dual-write → backfill → switch reads → drop later) with a rollback window that is never violated.
- [ ] M6: Produce a lock-time and backfill-duration analysis for a real 400M-row table and prove `lock_timeout` + concurrent DDL works under load.
- [ ] M7: Convert a real pipeline to GitOps with digest promotion, secret references, and demonstrate drift detection on a manual change.

---

## Anti-Goals

- Rebuilding per environment.
- Configuration or secrets baked into images.
- Rolling a user-facing change to 100% with no SLO gate.
- Canary steps chosen by feel rather than sample size.
- Feature flags with no owner and no expiry.
- A `DROP COLUMN` in the same release that stops using it.
- DDL without a `lock_timeout`.
- A one-shot backfill of hundreds of millions of rows.
- Treating "rollback is one command" as true without testing it.
- Secrets available to jobs triggered by untrusted PRs.

---

## Interview Lens

- "How do you roll back a bad release safely?"
- "How do you decide how long a canary runs at 1%?"
- "How do you change a database column without downtime?"
- "What is build-once-promote and why does it matter?"
- "How do you know your pipeline is fast enough that people use it?"

---

## 30-Day Plan

- **Week 1** — THEORY + ARCHITECTURE_DECISIONS: artifact promotion, pipeline design, deployment strategies; hands-on with digest pinning and stage timing. M1–M2.
- **Week 2** — EXERCISES: canary sizing, migration lock math, rollback budget; QUIZ to 13/15; FLASHCARDS daily. M3–M4.
- **Week 3** — MINI_PROJECT: build the pipeline, the canary analysis, the expand-contract migration, and the GitOps promotion. M5–M7.
- **Week 4** — REAL_WORLD_PROJECT war story; write a release-safety standard; teach-back: "our blast radius and rollback time, defended" in 10 minutes.

---

## Artifacts you should be able to show

1. A reproducibility proof (two builds, one digest) plus a digest-pinned pipeline.
2. A pipeline stage-timing report with a pre-merge feedback target.
3. A canary configuration with a pre-declared analysis and a measured promotion and reversal.
4. An expand-contract migration runbook with lock and backfill arithmetic.
5. A rollback-time measurement, published as an SLO.
6. A GitOps promotion flow with drift detection demonstrated.

---

## Done = You Can

- State a release's blast radius, detection window, and rollback time before shipping it.
- Explain why a particular DDL is or is not safe under load.
- Design a canary step that has the statistical power to detect the regression you care about.
- Say when rollback is unavailable and what the fix-forward path is instead.
