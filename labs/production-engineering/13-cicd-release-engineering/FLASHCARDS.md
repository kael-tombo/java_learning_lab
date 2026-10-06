# Lab 13: CI/CD Pipelines & Release Engineering — Flashcards

~60 cards. Most answers are a number or a policy.

---

## Build & artifact

Q: "Build once, promote the same artifact" — why?
A: A rebuild can differ (dependency resolution, timestamps, base image digest, embedded config). Promotion must move the same sha256/digest so what you tested is what ships.

Q: Verify it?
A: Print `sha256sum` of the jar and the image digest in the pipeline; have the deploy step assert the digest matches the artifact the tests ran against.

Q: What must NOT be baked into the image?
A: Environment, secrets, feature configuration, hostnames, anything environment-specific. Configuration is runtime (env vars, mounted config, flag service).

Q: Pin the base image by?
A: Digest, not a floating tag. A tag like `eclipse-temurin:21-jre` changes under you.

Q: Reproducible build check?
A: Same source + same toolchain digest + same dependency lock ⇒ same digest. Verify by building twice in a clean environment and comparing.

Q: Which pipeline steps gate a merge?
A: Compile, unit tests, static analysis, dependency/secret scan, and the fast contract tests. Everything else can run post-merge.

Q: Target pipeline latency?
A: Fast feedback < ~10 min (compile + unit), full pipeline < ~20 min. Measure queue wait separately — the wait is often the real cost.

Q: Cache key inputs?
A: Lockfile + toolchain/JDK/base-image digest + build flags + plugin versions. Keying on the source file alone gives stale-artifact flakes.

Q: Maven vs Gradle caching?
A: Maven: `.m2` cached keyed on the checksum of the effective dependency set (or `pom.xml`). Gradle: `gradle.lockfile` + build cache. Never cache only on the branch.

Q: Non-hermetic step to look for?
A: Anything that reads the current date, hostname, git SHA, or resolves "latest" — these make builds irreproducible.

---

## Quality gates

Q: Which gates block a merge?
A: Fast, deterministic, high-signal: compile, unit tests, SAST, dependency scan, secret scan, formatting/licence. Slow or flaky suites belong post-merge.

Q: Test pyramid proportion?
A: Many fast unit tests, fewer integration tests, fewest end-to-end. E2E is the most expensive signal per bug found.

Q: Coverage as a gate?
A: Useful as a *ratchet* (never decrease; require coverage on changed lines), harmful as an absolute percentage target (invites meaningless tests).

Q: Flaky test policy?
A: Quarantine, fail loudly, fix or delete within a time limit. A retried-in-CI flake is a hidden production bug.

Q: Dependency scan gate threshold?
A: Fail on HIGH/CRITICAL *with a fix available*; route the rest to a backlog with an owner and a date. Failing on unfixable findings trains people to ignore the gate.

Q: SAST in the pipeline vs IDE?
A: Both: IDE/quick feedback for the developer, pipeline as the enforcement point.

Q: Why gate on a documented, pre-declared SLO comparison in canaries?
A: Because the decision rule must exist before the data arrives; otherwise it becomes a judgement call after the fact.

---

## Deployment strategies

Q: Recreate?
A: Full downtime, new version everywhere. Almost never appropriate.

Q: Rolling update availability?
A: `available = replicas − maxUnavailable`. `maxUnavailable: 0, maxSurge: 1` gives 100% availability at the cost of one extra pod's resources.

Q: Rolling update risk?
A: All instances end up on the new code within minutes; there is no automatic signal for "this is subtly wrong". Availability yes, blast radius no.

Q: Blue/green?
A: Two full environments; switch traffic atomically. Instant rollback, but doubles capacity cost and requires schema compatibility both ways.

Q: Canary?
A: Route a small percentage (or a cohort) to the new version, compare against the control, then expand. Limits blast radius; requires enough traffic at each step for statistical validity.

Q: Recreate vs blue/green vs rolling vs canary — when each?
A: Recreate: never, except batch. Rolling: default for trusted changes. Blue/green: high-risk change with instant rollback needs. Canary: user-facing change you are unsure about.

Q: Minimum canary duration?
A: Enough to accumulate a statistically meaningful sample and at least one traffic cycle. Below a few thousand requests per variant, latency/error comparison is noise.

---

## Feature flags

Q: Flag's purpose?
A: Separate deploy from release; enable per cohort/percentage; kill without a deploy.

Q: Flag without an expiry?
A: Debt with a toggle. Every flag needs an owner and a removal date; a CI check should flag long-lived flags.

Q: Reading a flag on the hot path?
A: Locally-cached evaluation with periodic refresh and a safe default — never a synchronous remote call per request.

Q: Flag types?
A: Release (short-lived, on/off), operational (kill switch, requires fast local evaluation), experiment (long-lived, assigned to a user stably), permission/config (long-lived, a different tool). Treating them all as one kind is how estates get stuck.

Q: Flag hygiene gates?
A: No flag without an owner and expiry; no flag read more than N times per request (cache the result); no flag whose default is "on" for a risky behaviour.

Q: Experiment assignment must be?
A: Sticky per user (hash of userId + flag key), so a user does not flip between variants.

---

## Databases

Q: Expand-contract?
A: Add (expand) → dual-write → backfill → switch reads (migrate) → drop old (contract), with the drop in a *later* release after the rollback window.

Q: Why must the schema work with old and new code simultaneously?
A: Rolling updates run both; rollback may redeploy the old version after the migration. So the schema must satisfy both, in both directions.

Q: Add column: which form is safe?
A: Nullable with no default (or a non-volatile default) so the old code, which does not know the column, keeps working.

Q: Rename column?
A: Never in one step. Add new, dual-write, migrate reads, drop old later — or use a view/compatibility layer.

Q: Backfill in one statement?
A: No — batch it (e.g. 1,000 rows per transaction with a pause) so it does not hold a long transaction or saturate replication.

Q: Index creation on a live table?
A: Use the concurrent form where available (`CREATE INDEX CONCURRENTLY` in PostgreSQL; online DDL in MySQL). Otherwise the table is locked for the build duration.

Q: `NOT NULL DEFAULT` on a large table?
A: Can take an `ACCESS EXCLUSIVE` lock for the rewrite (version-dependent) — always verify your database's behaviour and always set a `lock_timeout` so it fails fast instead of queueing every query.

Q: Migration safety gates?
A: `lock_timeout` set, no destructive DDL in the same release as the code that stops using the column, review for long transactions, backfill batch size checked, and a stated rollback plan.

Q: Feature-flag a data change?
A: Prefer expand-contract. A flag around a dual-write path is fine (old path writes old column, new writes both); a flag that chooses which *query* to run is dangerous if both must be correct.

---

## Rollback

Q: When is rollback available?
A: Only when the previous artifact can read the current schema and state. Destructive migrations, data transformations, and contract breaks remove the option — decide before you write the migration.

Q: Time to rollback as a design target?
A: Measure it and treat it as an SLO. If rollback takes longer than fix-forward for your class of change, plan for fix-forward.

Q: Rollback of a bad canary?
A: Automatic, on a pre-declared SLO breach. This must not require a human at 03:00.

Q: Forward-fix vs rollback: when fix-forward?
A: When rollback is unsafe (schema/data/contract change already applied) and the fix is small. Then rollback of the *next* release, not this one.

---

## GitOps

Q: GitOps definition?
A: The desired state lives in Git as code; a controller continuously reconciles the cluster to it. Git is the source of truth and the audit record.

Q: Drift?
A: Live state differs from Git — a manual `kubectl edit`, a controller failure, or an out-of-band change. Reconciliation detects and reverts it.

Q: What is the real benefit of GitOps, beyond the sync tool?
A: Versioned, reviewed, auditable changes with automatic detection of manual intervention. Argo CD/Flux are the mechanism, not the point.

Q: Sync waves / progressive sync?
A: Ordered batches with health checks and automatic abort — progressive delivery expressed declaratively.

Q: Secrets in GitOps?
A: Never plaintext. Reference an external secret store (External Secrets Operator, SOPS/age, sealed secrets) and let Git hold only the reference.

Q: Image tags in GitOps — mutable or digest?
A: Digests, updated by an automated process that bumps the manifest after an image is promoted. That keeps Git as the record.

---

## Pipeline mechanics

Q: Parallelise what?
A: Independent checks (SAST, dependency scan, secret scan, unit tests on unaffected modules). Sequentialise only real dependencies.

Q: Matrix builds?
A: Test across JDK versions, OS, and architectures — and use the matrix to *find* failures, not to multiply hours.

Q: Self-hosted runner security?
A: Ephemeral runners per job. A persistent runner executing untrusted PR code is remote code execution on your build host.

Q: Untrusted PR code in a pipeline with secrets?
A: Never expose secrets to jobs triggered by forks/incoming PRs. Build without secrets; use OIDC-federated, short-lived credentials for deploys from trusted branches only.

Q: Pipeline as code?
A: Lint it, version it, test it. A pipeline change is as dangerous as an application change.

Q: Required status checks?
A: Enforce them on the protected branch so the pipeline cannot be bypassed.

Q: Deploy gating on environment?
A: Manual approval is acceptable for high-risk environments and should be a *pre-declared* rule, not an ad-hoc decision.

---

## Observability of the pipeline itself

Q: Which delivery metrics?
A: Lead time for changes, deployment frequency, change failure rate, time to restore service (the four DORA measures), plus per-stage pipeline duration and queue time.

Q: Which release metric matters most for risk?
A: Change failure rate and time-to-restore. Deployment frequency is a vanity metric if the failure rate is high.

Q: What to measure for canaries?
A: Per-variant request count, error rate, p95/p99 latency, and saturation (CPU/throttle/queue) — plus the decision that was taken and why.

Q: Rollout duration target?
A: Slow enough that each step has statistical validity, fast enough to finish inside the change window. For user-facing changes: canary 5–10 min, 25%, 50%, 100% with SLO gates at each step.

---

## Numbers and defaults to memorize

Q: Fast feedback target?
A: < ~10 min for compile + unit tests.

Q: Full pipeline target?
A: < ~20 min.

Q: Canary steps?
A: 1% → 5% → 25% → 50% → 100%, each gated on SLO comparison with a minimum sample.

Q: Canaries per step?
A: Seconds to a few minutes, but long enough for a minimum sample (thousands of requests) and one traffic cycle.

Q: Default `maxSurge` for a Java service?
A: 1 pod (with `maxUnavailable: 0` for zero downtime), and verify the memory budget can absorb it (Lab 07).

Q: Migration batch size for a backfill?
A: ~1,000 rows per transaction, tuned to keep each transaction under a second.

Q: Feature flag removal deadline?
A: 30–90 days, enforced by a CI check.

Q: Artifact retention?
A: Keep every promoted artifact for the rollback window (≥ 30 days) plus longer for anything under dispute.

Q: Time-to-rollback budget?
A: Target < 10 minutes from decision to restored service, measured and published.
