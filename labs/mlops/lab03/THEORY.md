# Model Registry & Versioning

**Track:** mlops  |  **Lab:** lab03  |  **Level:** Intermediate

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

Once several models are in production, 'which one is serving, which one should, and what produced it' becomes a question with no good answer unless you manage versions deliberately.

Model registries are where lineage, promotion and rollback become operational. Getting the stage model right prevents the two classic failures: shipping an unreviewed model and losing the ability to roll back.

## 2. Learning Objectives

- Model model versions, stages and their transitions explicitly
- Define what makes a version promotable and encode it as a gate
- Implement champion/challenger promotion with shadow evaluation
- Guarantee atomicity so two promotions cannot race
- Design lineage from a registry entry back to run, data and code
- Plan and rehearse rollback as a first-class operation

## 3. Core Concepts

### 3.1 Versions, stages and aliases

A version is immutable: same bytes, same hash, forever. A stage is a pointer to a version. Separating them means promotion is a pointer move, not a copy, which makes rollback instant and auditable. Never mutate a published version in place.

### 3.2 Champion and challenger

The champion serves. The challenger shadows it, scoring live traffic without affecting decisions. Promotion compares the two on matured labels, so the decision uses evidence rather than an offline metric that may not travel.

### 3.3 Gates, not opinions

A promotion gate is a declarative check: metrics within tolerance, lineage complete, fairness review signed off, latency budget met. Encoding the gate means no promotion depends on how confident the requester feels on a Friday evening.

### 3.4 Atomicity and concurrency

Two promotions racing will corrupt the stage pointers. Use a compare-and-set on the expected current version, or a lock, so the second promotion fails loudly instead of silently overwriting. This is a correctness bug, not a taste question.

### 3.5 Lineage and reproducibility

A registry entry should point back to the tracking run, the data version, the commit and the evaluation report. Without that, a rollback three months later needs archaeology. The pointer chain is what makes rollback safe.

### 3.6 Deprecation and retention

Registry growth is unbounded. Define what happens to a deprecated version (kept for rollback for N days, then archived, never deleted while a pointer can still reach it) and enforce it in the service rather than in documentation.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `stage -> version (atomic pointer)` | Stage model | promotion is a pointer move |
| `shadow_delta = metric(challenger) - metric(champion)` | Shadow comparison | on matured labels |
| `promote if delta > -eps and all gates pass` | Gate | declarative, reviewable |
| `cas(stage, expected, next)` | Compare-and-set | prevents promotion races |
| `rollback: stage -> previous(champion)` | Rollback | instant and audited |
| `retention(days, reachability)` | Retention policy | never delete a reachable version |

## 5. How the Pieces Fit Together

1. Train and track the run (Lab 02), producing an immutable artifact with a content hash.

2. Register the artifact with a version, lineage (run, data version, commit) and evaluation report.

3. Deploy to shadow; it scores live traffic without affecting decisions.

4. Evaluate the challenger against the champion on matured labels for a fixed window.

5. Run the gate: metrics within tolerance, lineage complete, sign-offs recorded.

6. Promote with compare-and-set; watch guardrails; roll back with one command if a guardrail breaches.

## 6. Assumptions and Invariants

- Published versions are immutable and content-hashed
- Stage transitions go through a service, not direct database edits
- Lineage is complete before a version can be staged
- Shadow evaluation runs long enough to mature labels
- Concurrency control is in place for concurrent promotions
- Retention never deletes a version a stage or alias can still reach

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Two promotions raced and production is now on an unvetted model | no compare-and-set on the stage pointer | use CAS on expected current version; the second promotion must fail loudly |
| A rollback needed the code commit and nobody had it | no lineage on the registry entry | lineage is a gate, not optional metadata |
| The challenger was promoted on an offline metric and got worse live | no shadow evaluation on matured labels | require a shadow window with matured-label comparison |
| A published version was edited in place | mutating an immutable artifact | versions are content-hashed; a change is a new version |
| Registry has 400 versions and nobody can find the champion | no stage model or aliases | use stages and aliases; archive by policy |
| Rollback itself failed because the artifact store was down | artifact not pinned locally | cache the current champion locally for fast rollback |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `AtomicReference / synchronized on the stage pointer` | compare-and-set style promotion |
| `record ModelVersion(String name, int version, String artifactHash, Lineage lineage)` | immutable registry entry |
| `EnumMap for stages` | explicit stage set with legal transitions |
| `java.nio.file.Files.copy with ATOMIC_MOVE` | publishing artifacts without half-written reads |
| `Duration-based retention sweep` | archiving unreachable versions on a schedule |

## 9. Where This Sits in the Larger System

- **mlops/lab02** produces the runs and metrics a registry entry points at.
- **mlops/lab05** and **lab06** deploy whatever the registry says is champion.
- **mlops/lab10** is where the shadow comparison and the promotion decision belong.
- **mlops/lab11** adds the sign-offs and audit trail the gate enforces.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Model model versions, stages and their transitions explicitly
- [ ] 0 — cannot yet — Define what makes a version promotable and encode it as a gate
- [ ] 0 — cannot yet — Implement champion/challenger promotion with shadow evaluation
- [ ] 0 — cannot yet — Guarantee atomicity so two promotions cannot race
- [ ] 0 — cannot yet — Design lineage from a registry entry back to run, data and code
- [ ] 0 — cannot yet — Plan and rehearse rollback as a first-class operation

## 11. Summary Checklist

- [ ] I can explain why versions are immutable and stages are pointers
- [ ] My promotion gate is declarative and enforced by a service
- [ ] Concurrent promotions cannot race
- [ ] Every entry has complete lineage
- [ ] Rollback is one command and has been rehearsed
- [ ] Retention never deletes a reachable version
