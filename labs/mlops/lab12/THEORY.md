# Infrastructure as Code for ML

**Track:** mlops  |  **Lab:** lab12  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. The Problem This Solves

The training cluster exists because someone clicked through a console once. Reproducing it, reviewing the change and proving what it actually contains are all manual, slow and unreliable.

ML infrastructure is ordinary cloud infrastructure with expensive accumulators and stateful stores attached. Managing it as code is what makes the platform reviewable.

## 2. Learning Objectives

- Express ML infrastructure as versioned, reviewable configuration
- Separate environment configuration from resource topology
- Model GPU and CPU pools with quota, priority and cost awareness
- Use workspaces and remote state so teams cannot collide
- Detect and prevent resource drift between code and reality
- Design a destroy-and-recreate path that is safe for stateful resources

## 3. Core Concepts

### 3.1 Code, not console

Console-created resources are invisible to review, untagged by intent and impossible to reproduce. The value of infrastructure as code is not automation; it is that a change becomes a reviewable diff with an author.

### 3.2 Topology versus configuration

Which resources exist (a GPU node pool, a bucket, a private subnet) is code. What values they hold (bucket names, instance counts, ARNs) are environment configuration. Mixing them means every environment needs a copy of the code, and the copies drift.

### 3.3 Stateful resources need a different lifecycle

A GPU pool is disposable; a feature store with production data is not. Recreating state means backups and a documented restore path. Most IaC disasters are stateful resources destroyed by a plan nobody read.

### 3.4 Quota and priority are policy

GPU hours are the scarce resource. A pool with a quota and a priority class turns 'the cluster is full' from an outage into a queue. Cost tags on every resource make chargeback possible without archaeology.

### 3.5 Drift detection is the missing half

Code says what should exist; reality says what does. Detecting and reporting drift is what keeps the two from diverging silently for months, and it is what makes 'approved by review' true rather than aspirational.

### 3.6 Workspaces and least privilege

Per-team state and per-team credentials prevent one team's apply from destroying another's resources. Least-privilege roles also mean a compromised pipeline cannot reach the production data lake.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `plan = f(code, state) -> resource_changes` | Plan semantics | the reviewable artifact |
| `drift = actual - desired` | Drift | difference between code and reality |
| `cost = sum(gpu_hours x rate + storage_gb x rate)` | Cost model | tagged per resource |
| `quota_used = sum(active_requests)` | Quota | the queueing constraint |
| `recovery_time = RTO, recovery_point = RPO` | Stateful SLOs | what recreate must preserve |
| `apply = state := plan` | Apply | atomic by region, reviewed before running |

## 5. How the Pieces Fit Together

1. Separate topology code from environment configuration and version both.

2. Create a per-team workspace with isolated state and least-privilege credentials.

3. Define pools with quota, priority and mandatory cost tags.

4. Run plan, review the diff, and record the reviewer with the apply.

5. Detect drift on a schedule and report divergence rather than silently correcting it.

6. Document the destroy-and-recreate path for stateful resources, including backups.

## 6. Assumptions and Invariants

- All infrastructure changes go through reviewed code, never a console
- Topology and environment configuration are in separate files
- Per-team state and credentials prevent cross-team collisions
- Every resource carries cost tags and a purpose tag
- Drift is detected on a schedule and reported to an owner
- Stateful resources have a documented backup and restore path

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Production destroyed by a plan nobody read | destructive plan applied without review | require review on plans, and forbid destroy on stateful resources without a restore check |
| Two environments diverge because the code was copied | topology and configuration in one file | parameterise environment configuration separately |
| Cluster full and nobody knows whose job is queued | no quota or priority | quotas and priority classes make the queue visible |
| GPU spend unattributable | resources without cost tags | mandatory tags enforced in the plan stage |
| Drift accumulates for months | no drift detection | scheduled drift detection with an owner per resource |
| One team's apply destroyed another's queue | shared state | per-team workspaces with isolated state |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `HOCON / properties for environment configuration` | keeps topology code environment-agnostic |
| `record Plan(List<ResourceChange> changes, int create, int update, int destroy)` | the reviewable diff as a typed value |
| `Diff computation on desired vs actual` | drift detection as a pure function |
| `Structured plan output (JSON)` | so a human or a bot reviews it before apply |
| `Immutable config classes for pools and quotas` | policy encoded in types, not comments |

## 9. Where This Sits in the Larger System

- **mlops/lab01** provisions the compute these pools back.
- **mlops/lab06** schedules onto the node pools this lab defines.
- **mlops/lab05** builds images into the registry this lab provisions.
- **mlops/lab03** stores artefacts in the storage this lab provisions.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Express ML infrastructure as versioned, reviewable configuration
- [ ] 0 — cannot yet — Separate environment configuration from resource topology
- [ ] 0 — cannot yet — Model GPU and CPU pools with quota, priority and cost awareness
- [ ] 0 — cannot yet — Use workspaces and remote state so teams cannot collide
- [ ] 0 — cannot yet — Detect and prevent resource drift between code and reality
- [ ] 0 — cannot yet — Design a destroy-and-recreate path that is safe for stateful resources

## 11. Summary Checklist

- [ ] No production resource was created in a console.
- [ ] Topology and environment configuration are separate.
- [ ] Every apply has a reviewable plan with a named reviewer.
- [ ] Resources carry cost and purpose tags.
- [ ] Drift is detected on a schedule.
- [ ] Stateful resources have a tested restore path.
