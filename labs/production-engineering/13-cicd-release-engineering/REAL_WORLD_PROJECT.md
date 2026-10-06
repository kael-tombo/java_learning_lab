# Lab 13: CI/CD Pipelines & Release Engineering — Real World Project

## Scenario: "The Migration That Locked the Table"

You are a platform engineer on a payments platform: 16 Spring Boot 3 services, Java 21, Kubernetes, PostgreSQL 15 primary (2 TB, 380M rows in `ledger_entries`), Argo CD, Jenkins for CI.

**The incident** — Tuesday 02:14, off-hours deploy window (chosen deliberately).

**What happened over 5 hours**:

1. **02:14** — Release of `ledger-writer` 3.2.0 begins. The release contains one migration: `ALTER TABLE ledger_entries ALTER COLUMN currency TYPE VARCHAR(8)`. On a 380M-row table with no default, in PostgreSQL this is a table rewrite — and it takes an `ACCESS EXCLUSIVE` lock for the duration.
2. **02:16** — Every query touching `ledger_entries` queues behind the lock. Connection pool exhaustion follows within 90 seconds. `ledger-writer`, `statement-service`, and `reporting` all start timing out. There is no alert on pool saturation; the first signal is a customer complaint at 02:31.
3. **02:31–02:52** — The deployer, on a call at 02:20, does not realise the migration is the cause. The application logs show connection timeouts, not SQL errors. They check the database and find 1,400 queries in `pg_locks` waiting on the `AccessExclusiveLock`. They kill the migration.
4. **02:52** — Killing the migration rolls it back, but 21 minutes of queued queries were simultaneously released and flooded the primary. CPU 100% for 4 more minutes.
5. **03:00** — Service restored, but only after 46 minutes of customer-visible failure.
6. **Wednesday** — The same team discovers three further facts that make it worse:
   - Their rollback was never tested. Reverting `ledger-writer` to 3.1.0 would have worked (the column type widening is backward compatible), but nobody knew that, so nobody tried it during the incident.
   - Their CI takes 47 minutes end-to-end, 31 of which are the integration suite, so engineers were shipping to a 02:00 window rather than shipping continuously.
   - They have 340 deployments in the last 90 days and a 19% change-failure rate. Every one of them was a full rollout to 100% with no canary.

**Your job over 4 weeks**: make releases safe. Reproducible builds with digest promotion, a pipeline whose feedback latency people will actually wait for, migrations that cannot lock a table, progressive delivery with machine analysis, and a rollback path that is tested rather than assumed.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Reconstruct and enumerate (Day 1–4)

### 1.1 Reconstruct the incident

Timeline with the lock arithmetic: query arrival rate × lock duration = queued queries; pool size = concurrent blockers; customer-impact start time.

**Deliverable 1 — Causal analysis** with the lock duration, the queue growth, the 17-minute detection gap explained by the missing pool-saturation alert, and the post-kill flood explained.

### 1.2 Pipeline audit

For all 16 services: stage durations, queue wait, test counts and flake rate, cache hit rate, artefact promotion model (rebuild per environment?), base image pinning, and whether deploys go through the same pipeline or by hand.

**Deliverable 2 — Pipeline audit** with per-stage timings for the three slowest services and a fleet-wide summary.

### 1.3 Release history audit

For the last 90 days: 340 deployments, rolled-back count, deployments that caused incidents, mean time to rollback, and for each incident whether rollback was attempted and whether it worked.

**Deliverable 3 — Release history audit** with change-failure rate, incident-to-deployment mapping, and the rollback-success table. This is your business case.

### 1.4 Migration inventory

Every migration in 16 services: type of DDL, table size, whether it takes a write lock, whether it has a `lock_timeout`, whether it is additive, and when the corresponding column is dropped relative to the code change.

**Deliverable 4 — Migration inventory** with a ranked list of migrations that would each have caused a similar incident. Estimate lock duration for each from table size.

---

## Phase 2 — Fix the pipeline (Day 4–8)

### 2.1 Build once, promote the digest

- One CI build per commit; the artifact is promoted through environments with its digest verified at each deploy step.
- Base images pinned by digest, with a weekly automated bump PR.
- No environment or secrets in the image.
- Artifact retention for at least 90 days.

**Deliverable 5 — Promotion model** implemented for all 16 services, with the digest assertion in the deploy step and a before/after table.

### 2.2 Restructure for feedback latency

Split every pipeline into:
- **Pre-merge (blocking)**: compile, unit tests, fast static analysis, dependency/secret scan, contract diff. Target < 10 minutes.
- **Post-merge (not blocking)**: full integration suite, load test, image build, staging deploy, smoke tests, canary.

Measure and publish queue wait separately.

**Deliverable 6 — Pipeline restructure** with before/after stage timings for the 16 services, and the new feedback-latency distribution (median, p85).

### 2.3 Eliminate flakiness

Inventory every retried or quarantined test. Fix or delete. Add a rule: a test may not be auto-retried in CI; a flake is a failing build with a known issue link.

**Deliverable 7 — Flake elimination report**: tests quarantined/deleted, CI minutes recovered, and the developer-override rate before/after (ask, then verify by watching for `--no-verify`).

---

## Phase 3 — Migrations that cannot lock a table (Week 2)

### 3.1 The migration standard

Every migration must:
- Set `lock_timeout` (e.g. 2s) and `statement_timeout`.
- Be additive: new column nullable, no type changes on populated columns, no renames.
- Use concurrent index creation where available.
- Backfill in batches outside the release, with a computed rate and a replica-lag guard.
- Drop old columns only in a later release, after the rollback window closes.
- Ship with a documented rollback story.

**Deliverable 8 — Migration standard** plus a CI check (`pgFormatter`/`psql` lint plus a custom rule set) that rejects non-additive DDL and missing `lock_timeout`.

### 3.2 Convert the `currency` migration

The incident migration becomes:

| Step | Release | Statement | Lock |
|---|---|---|---|
| 1 | today | `SET lock_timeout='2s'` | none |
| 2 | today | `ADD COLUMN currency_v2 VARCHAR(8)` (nullable) | metadata-only, instant |
| 3 | same release | dual-write both columns | n/a |
| 4 | batched job | backfill 380M rows at a computed rate | row locks only, small batches |
| 5 | +1 week | switch reads to `currency_v2` | none |
| 6 | +30 days | `DROP COLUMN currency` | metadata-only |

Backfill arithmetic: batch 10,000 rows, 250 ms per transaction, 250 ms pause → `20,000 rows/s` → `380M / 20,000 = 5.3 h`. Run it with a replica-lag guard that pauses above 30 s lag.

**Deliverable 9 — Converted migration** run under production-shaped load in staging, with lock timings, backfill duration, replica lag curve, and the full rollback-validity table.

### 2.3 Rewrite history audit

Find every historical migration still in the tree that is destructive with no `lock_timeout`, and produce a remediation plan (recreate the table in shadow, cut over, archive the old migration) for the top 10.

**Deliverable 10 — Historical migration remediation plan** with per-migration lock estimates and sequencing.

---

## Phase 4 — Progressive delivery (Week 2–3)

### 4.1 Canary with pre-declared analysis

Rollouts for all 16 services, with an analysis template gating on:
- error rate (absolute and relative to control),
- p99 latency (absolute SLO and relative),
- saturation (CPU throttling, pool wait, queue depth),
- and for `ledger-writer` and `payment-service`, a **business** SLI (successful ledger entries per minute).

Steps: 1% (5 min) → 5% (5 min) → 25% (5 min) → 50% (3 min) → 100%, with the step durations derived from the sample-size calculation.

**Deliverable 11 — Rollout configuration** for all 16 services, with the sample-size calculation behind each pause duration and the analysis queries with thresholds.

### 4.2 Automatic rollback

`abortScaleDownDelaySeconds`, `autoPromotionEnabled` rules, and a documented rule: on analysis failure, Argo aborts and the stable service keeps serving. No human in the loop at 03:00.

**Deliverable 12 — Automatic rollback policy**, tested by deploying four deliberately bad releases (error, latency, saturation, business-SLO regression).

### 4.3 Rollback path testing

For all 16 services, run a rollback drill: deploy a bad version, roll back, verify, measure. Record `T_rollback = detect + decide + command + rollout + verify`.

**Deliverable 13 — Rollback drill report**: per-service rollback time, whether the database state permits rollback, and the list of services where rollback is *unavailable* and fix-forward is the only option.

---

## Phase 5 — GitOps (Week 3)

- Argo CD for all environments; `automated` sync with self-heal and prune.
- Image digests in Git; a promotion job writes the digest after the canary succeeds.
- Secrets by reference (External Secrets + existing vault); never in Git.
- Progressive sync waves per service dependency order.
- Sync windows and rate limits so a bad image cannot fan out to 16 services in 60 seconds.

**Deliverable 14 — GitOps migration** with the promotion flow, drift detection demonstration (manual `kubectl edit` reverted with timing), the audit trail, and the fan-out protection measure.

---

## Phase 6 — Feature flag hygiene (Week 3–4)

- Inventory every flag in the estate: type, owner, creation date, read frequency, evaluation locality.
- Classify: release (short), operational/kill switch (needs local evaluation), experiment (needs sticky assignment), permission/config.
- Move remote config reads off the hot path into locally-cached evaluation with a safe default.
- CI rule: a new flag without an owner and an expiry fails.
- Delete or convert every flag older than 90 days.

**Deliverable 15 — Flag hygiene report**: flag inventory, the state-space analysis per service (`Π flags`), deleted/converted counts, and the hot-path evaluation fix.

---

## Phase 7 — Prove it (Week 3–4)

| Scenario | Injection | Success criteria |
|---|---|---|
| S1 | Replay the `currency` migration on a 380M-row table under 4,000 writes/s | completes with no lock; zero blocked writes; p99 unaffected |
| S2 | Same, with a deliberately non-additive DDL (blocked by CI) | cannot be deployed |
| S3 | Deploy a release that 5xx's on 3% of requests | caught at 5% in < 5 min; automatic rollback; < 1% of traffic affected |
| S4 | Deploy a release with +300 ms p99 | caught at 25% by the latency gate |
| S5 | Deploy a release with a memory misconfiguration | caught by the saturation gate |
| S6 | Deploy a release that breaks the business SLI (entries still "succeed" but fewer) | caught by the business SLI, not by HTTP metrics |
| S7 | Manual `kubectl edit` in prod | reverted by self-heal within the sync interval; Git unchanged |
| S8 | Mutable tag push | blocked at admission by digest-pinned policy |
| S9 | A PR that reintroduces a destructive migration | blocked by CI |
| S10 | Game day: bad release deployed during business hours with the on-call | machine detects in under 5 min; responder's time-to-diagnosis recorded |
| S11 | Rollback drill on every service | rollback time published; services without a rollback option listed |

**Deliverable 16 — Release safety test report** with all eleven scenarios, measured times, and fixes for anything missed.

---

## Phase 8 — Quantify and institutionalize (Week 4)

| Metric | Before | After |
|---|---|---|
| Change failure rate (90 days) | 19% | target < 5% |
| Pipeline feedback latency (median / p85) | 47 min | < 8 min / < 12 min |
| Deployments that reached 100% before detection | all | ~0 (canary or metric catches at ≤ 25%) |
| Mean time to rollback | not measured; ~25 min | < 8 min, published |
| Services with a tested rollback path | 0 / 16 | 16 / 16 |
| Services where rollback is unavailable | unknown | known and documented, with fix-forward playbooks |
| Migrations that can lock a table | unknown | 0 (CI-enforced) |
| Destructive DDL shipped ahead of code | ≥ 6 (12 months) | 0 |
| Artifacts rebuilt per environment | 16 services × 3 envs | 0 (one build, digest promoted) |
| Detections from 02:14-style events | 17 min (customer complaint) | < 60 s (pool saturation alert) |
| Flaky tests bypassed | ~11 known | 0 |
| Release window | 02:00 batch | continuous, any hour |
| Flag state space per service | unmeasured | measured and bounded by expiry |

Institutionalize: the migration standard and its CI check become platform policy; progressive delivery is the default template; digest-pinned GitOps is mandatory; a new service cannot be created without a canary analysis, a tested rollback, and a migration policy.

**Deliverable 17 — Business case + institutionalization**, presented with the incident cost ($ figures from your incident record) traded against the pipeline and platform investment.

---

## Deliverables checklist

- [ ] Phase 1 causal analysis, pipeline audit, release history audit, migration inventory.
- [ ] Phase 2 digest promotion, pipeline restructure, flake elimination.
- [ ] Phase 3 migration standard + CI check, converted migration under load, historical remediation plan.
- [ ] Phase 4 canary analysis, automatic rollback, rollback drills.
- [ ] Phase 5 GitOps migration with drift detection and fan-out protection.
- [ ] Phase 6 flag hygiene.
- [ ] Phase 7 eleven-scenario release safety test report.
- [ ] Phase 8 before/after business case + institutionalization.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Diagnosis | "The migration locked the table" | Lock duration, queue growth, pool exhaustion, 17-min detection gap, post-kill flood explained |
| Build | "We tag images" | Digest promotion with verification, reproducibility proven, no env/secrets in image |
| Pipeline | "It's slow" | Stage and queue timings, pre/post-merge split, flake elimination with override-rate evidence |
| Migrations | "We added a timeout" | Expand-contract timeline, concurrent DDL, computed backfill rate, rollback-validity table, historical audit |
| Canary | "We deploy 10% first" | Pre-declared analysis on error + latency + saturation + business SLI, step durations from sample-size math |
| Rollback | "kubectl rollout undo" | Every service drilled; time published; unavailable rollbacks named with fix-forward playbooks |
| GitOps | "We use Argo" | Digest-in-Git promotion, secret references, drift detection with timing, fan-out protection |
| Proof | "Load test" | Replays the actual 380M-row migration under load plus four bad releases and a game day |
| Economics | Technical only | Change-failure rate, feedback latency, detection time, and incident cost traded against platform investment |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Kubernetes — `concepts/workloads/pods/pod-lifecycle` (container states, probes, restart/back-off) and `tasks/configure-pod-container/configure-pod-configmap` / Secrets** — https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/ — the authoritative source for the deployment mechanics the Lab 07 material builds on and for the graceful-termination sequence (preStop, SIGTERM, `terminationGracePeriodSeconds`, endpoint removal) that determines whether a rollback rollout causes user-visible 502s. Also `kubernetes.io/docs/tasks/configure-pod-container/assign-cpu-resource/` for the CFS throttling semantics used in the canary saturation gate. Verify the current probe/termination defaults and the `kubectl rollout undo` behaviour for your Kubernetes version.
2. **Argo Rollouts and Argo CD documentation** — https://argo-rollouts.readthedocs.io/en/stable/ and https://argo-cd.readthedocs.io/en/stable/ — the authoritative source for canary step semantics (`setWeight`, `pause`, `analysis` templates, `startingStep`, `abortScaleDownDelaySeconds`), automatic abort on analysis failure, and `AnalysisTemplate`/`RunAnalysis` provider configuration for Prometheus queries. Also `argocd.argoproj.io` docs on `image:` digest support in Helm values, `automated` sync with self-heal/prune, and sync windows. Verify the exact CRD field names and version-specific behaviours — these APIs change between minor releases and a stale config fails silently or is rejected.

Additional anchors worth verifying: PostgreSQL 15/16 lock behaviour for the specific DDL in your estate — `ALTER TABLE ... ALTER COLUMN TYPE` rewrites the table and takes `ACCESS EXCLUSIVE` unless the change is binary-coercible, and the exact rewrite/lock semantics differ between versions and between `ADD COLUMN` with and without a default; `CREATE INDEX CONCURRENTLY`'s restriction on `transaction blocks` and the need to drop invalid indexes left by a failed concurrent build; and your CI/CD vendor's actual default queue-wait and cache-key behaviour, which is usually the dominant contributor to perceived pipeline latency.

---

## Reflection questions

1. The migration took an `ACCESS EXCLUSIVE` lock on a 380M-row table. Why did the detection take 17 minutes, and which single alert would have caught it in under a minute?
2. Nobody knew rollback was available. What would make rollback capability a *tested, declared* property rather than an assumption?
3. Their 02:00 deploy window was a workaround for a 47-minute pipeline. What is the right order of operations: shrink the pipeline, or deploy more often?
4. A 19% change-failure rate over 340 deployments means roughly one bad release a week. Which of the eleven controls in this lab would have caught the most of them, and why?
5. If you could only ship one change next week — canary analysis, digest promotion, or the migration standard — which one, and what does the arithmetic say?
