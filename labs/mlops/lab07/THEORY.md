# CI/CD for ML Pipelines

**Track:** mlops  |  **Lab:** lab07  |  **Level:** Intermediate

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

A model that takes hours to evaluate cannot wait for a code review cycle, and a pipeline that only runs after merge discovers breakage hours later, when the data has moved.

ML CI/CD inverts the usual shape: unit tests take seconds, but data, features and model smoke runs must also gate every change, or the pipeline is testing the wrong thing.

## 2. Learning Objectives

- Design CI stages for code, data, features and model changes
- Keep the pre-merge pipeline fast enough that people wait for it
- Separate a fast smoke suite from a slow nightly evaluation suite
- Cache and version artefacts so pipeline time does not grow with the repo
- Make the evaluation suite a gate, not a report
- Handle retraining and deployment as separate concerns from CI

## 3. Core Concepts

### 3.1 Four change types, four responses

Code changes, data changes, feature changes and hyperparameter changes have different risk profiles. Treating them identically produces either slow pipelines or blind spots. A feature change needs point-in-time tests; a hyperparameter change needs a full evaluation.

### 3.2 Fast gates and slow gates

Pre-merge must finish in minutes: compile, unit tests, a tiny model smoke run on a fixture, schema and contract checks. The expensive evaluation runs on merge as a nightly or pre-release job. Putting the slow part in the pull request is how teams end up bypassping CI.

### 3.3 Artefact versioning over rebuilding

Cache the training data snapshot, the feature materialisation and the dependency cache by content hash. Rebuilding the world on every commit is why ML pipelines get skipped under deadline pressure.

### 3.4 Evaluation suites as gates

A metric regression check belongs in CI: 'accuracy must not drop more than 0.5% on the frozen eval set'. A dashboard nobody blocks on is a report, not a gate. The gate needs a frozen set to be meaningful.

### 3.5 Data and code contracts

Schema contracts catch breaking changes at the boundary. Data contracts catch upstream changes that silently break a feature. Both belong in pre-merge, where the feedback is cheap.

### 3.6 Deployment is not CI

CI proves the change is sound. Promotion to production needs shadow evaluation and a gate from the registry (Lab 03). Conflating them means either slow merges or unreviewed production.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `pipeline_time = code + data + features + smoke` | Pre-merge budget | must fit a reviewer's patience |
| `delta = metric(candidate) - metric(baseline)` | Gate evaluation | on a frozen eval set |
| `promote if delta > -epsilon` | Regression gate | declared, not observed |
| `cache_key = hash(commit, data_version, lockfile)` | Cache validity | content-addressed, not time-based |
| `smoke_coverage = cases / total_cases` | Fixture size | small but representative |
| `time_to_detect = merge_to_alert` | Pipeline value | the number CI optimises |

## 5. How the Pieces Fit Together

1. On push: build, unit test, lint, schema and contract checks — all under a few minutes.

2. Train a tiny model on a fixture and assert it learns; catches broken feature code.

3. On merge to main: full training on the real snapshot, with cached data and features.

4. Run the evaluation suite on a frozen set; fail the build on a regression beyond epsilon.

5. Register the artefact and deploy to shadow, not to production.

6. Promotion to production happens through the registry gate, outside CI.

## 6. Assumptions and Invariants

- Pre-merge pipeline finishes in minutes so people wait for it
- The evaluation set is frozen and versioned so deltas are comparable
- Data and dependency caches are content-addressed, not time-based
- Schema and data contracts run before expensive jobs
- CI proves soundness; the registry gate decides promotion
- Pipeline duration and failure rate are themselves monitored

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| Engineers merge without waiting for CI | pipeline too slow, usually data or training in the pull request | move expensive work to post-merge; keep pre-merge under minutes |
| Accuracy dropped 3% and CI was green | no evaluation gate on a frozen set | add a regression gate with a declared epsilon |
| Cache serves stale data | cache keyed by commit time rather than content hash | key caches by data version and lockfile hash |
| Nightly broke because a feature changed | no point-in-time or schema test for the feature view | add contract tests per feature view in pre-merge |
| A broken upstream schema merged cleanly | no data contract at the boundary | schema contracts in CI with a failing example |
| Deployment happened from CI on merge to main | CI promoting directly | shadow deploy in CI; promotion through the registry gate |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `JUnit 5 + a tiny smoke fixture` | the fast gate that actually catches broken feature code |
| `Content hash for cache keys` | SHA-256 over commit, data version and lockfile |
| `System.getenv for pipeline parameters` | commit, data version, epsilon in config not code |
| `record GateResult(String name, boolean passed, double delta)` | each gate reported with its numbers |
| `Micrometer timers around stages` | pipeline duration as a first-class metric |

## 9. Where This Sits in the Larger System

- **mlops/lab02** stores the runs CI produces.
- **mlops/lab09** provides the data and schema gates this pipeline calls.
- **mlops/lab03** owns promotion; CI only deploys to shadow.
- **mlops/lab01** runs the full DAG on merge; CI runs its smoke subset.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — Design CI stages for code, data, features and model changes
- [ ] 0 — cannot yet — Keep the pre-merge pipeline fast enough that people wait for it
- [ ] 0 — cannot yet — Separate a fast smoke suite from a slow nightly evaluation suite
- [ ] 0 — cannot yet — Cache and version artefacts so pipeline time does not grow with the repo
- [ ] 0 — cannot yet — Make the evaluation suite a gate, not a report
- [ ] 0 — cannot yet — Handle retraining and deployment as separate concerns from CI

## 11. Summary Checklist

- [ ] Pre-merge finishes in minutes and people wait for it.
- [ ] The evaluation suite gates the build with a declared epsilon.
- [ ] Caches are content-addressed.
- [ ] Schema and data contracts run before expensive jobs.
- [ ] CI deploys to shadow; promotion goes through the registry.
- [ ] Pipeline duration and failure rate are monitored as metrics.
