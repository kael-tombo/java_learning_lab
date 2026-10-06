# CI/CD for ML Pipelines - Flashcards (60 cards)

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

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | What should run in pre-merge? | Compile, unit tests, schema and contract checks, and a tiny smoke training run on a fixture. |
| 2 | What should not run in pre-merge? | Full training and full evaluation on the real dataset; they belong after merge. |
| 3 | Why a smoke training run? | It catches broken feature code and broken pipelines, which unit tests cannot. |
| 4 | What is an evaluation gate? | A check that a candidate's metric on a frozen eval set does not regress beyond a declared epsilon. |
| 5 | Why must the eval set be frozen? | So deltas between runs are comparable; a moving eval set makes the gate meaningless. |
| 6 | How should caches be keyed? | By content hash of commit, data version and lockfile, never by time. |
| 7 | What is a data contract? | An agreement on the shape and semantics of upstream data, checked in CI so breaking changes fail fast. |
| 8 | Why does CI not deploy to production? | Promotion needs shadow evaluation and a registry gate; CI only proves soundness. |
| 9 | What is Four change types, four responses? | Code changes, data changes, feature changes and hyperparameter changes have different risk profiles. |
| 10 | What is Fast gates and slow gates? | Pre-merge must finish in minutes: compile, unit tests, a tiny model smoke run on a fixture, schema and contract checks. |
| 11 | What is Artefact versioning over rebuilding? | Cache the training data snapshot, the feature materialisation and the dependency cache by content hash. |
| 12 | What is Evaluation suites as gates? | A metric regression check belongs in CI: 'accuracy must not drop more than 0. |
| 13 | What is Data and code contracts? | Schema contracts catch breaking changes at the boundary. |
| 14 | What is Deployment is not CI? | CI proves the change is sound. |
| 15 | In this lab, what does `pipeline_time = code + data + features + smoke` mean? | Pre-merge budget: must fit a reviewer's patience |
| 16 | In this lab, what does `delta = metric(candidate) - metric(baseline)` mean? | Gate evaluation: on a frozen eval set |
| 17 | In this lab, what does `promote if delta > -epsilon` mean? | Regression gate: declared, not observed |
| 18 | In this lab, what does `cache_key = hash(commit, data_version, lockfile)` mean? | Cache validity: content-addressed, not time-based |
| 19 | In this lab, what does `smoke_coverage = cases / total_cases` mean? | Fixture size: small but representative |
| 20 | In this lab, what does `time_to_detect = merge_to_alert` mean? | Pipeline value: the number CI optimises |
| 21 | You see 'Engineers merge without waiting for CI' in production. What is the cause and the fix? | pipeline too slow, usually data or training in the pull request Fix: move expensive work to post-merge; keep pre-merge under minutes |
| 22 | You see 'Accuracy dropped 3% and CI was green' in production. What is the cause and the fix? | no evaluation gate on a frozen set Fix: add a regression gate with a declared epsilon |
| 23 | You see 'Cache serves stale data' in production. What is the cause and the fix? | cache keyed by commit time rather than content hash Fix: key caches by data version and lockfile hash |
| 24 | You see 'Nightly broke because a feature changed' in production. What is the cause and the fix? | no point-in-time or schema test for the feature view Fix: add contract tests per feature view in pre-merge |
| 25 | You see 'A broken upstream schema merged cleanly' in production. What is the cause and the fix? | no data contract at the boundary Fix: schema contracts in CI with a failing example |
| 26 | You see 'Deployment happened from CI on merge to main' in production. What is the cause and the fix? | CI promoting directly Fix: shadow deploy in CI; promotion through the registry gate |
| 27 | Which Java API is the backbone of: the fast gate that actually catches broken feature code | `JUnit 5 + a tiny smoke fixture` |
| 28 | Which Java API is the backbone of: SHA-256 over commit, data version and lockfile | `Content hash for cache keys` |
| 29 | Which Java API is the backbone of: commit, data version, epsilon in config not code | `System.getenv for pipeline parameters` |
| 30 | Which Java API is the backbone of: each gate reported with its numbers | `record GateResult(String name, boolean passed, double delta)` |
| 31 | Which Java API is the backbone of: pipeline duration as a first-class metric | `Micrometer timers around stages` |
| 32 | Why does Four change types, four responses matter operationally? | Code changes, data changes, feature changes and hyperparameter changes have different risk profiles. |
| 33 | Why does Fast gates and slow gates matter operationally? | Pre-merge must finish in minutes: compile, unit tests, a tiny model smoke run on a fixture, schema and contract checks. |
| 34 | Why does Artefact versioning over rebuilding matter operationally? | Cache the training data snapshot, the feature materialisation and the dependency cache by content hash. |
| 35 | Why does Evaluation suites as gates matter operationally? | A metric regression check belongs in CI: 'accuracy must not drop more than 0. |
| 36 | Why does Data and code contracts matter operationally? | Schema contracts catch breaking changes at the boundary. |
| 37 | Why does Deployment is not CI matter operationally? | CI proves the change is sound. |
| 38 | In the CI/CD for ML Pipelines pipeline, what happens next? On push: build, unit test, lint, schema and contract checks ... | On push: build, unit test, lint, schema and contract checks — all under a few minutes. |
| 39 | In the CI/CD for ML Pipelines pipeline, what happens next? Train a tiny model on a fixture and assert it learns; catche... | Train a tiny model on a fixture and assert it learns; catches broken feature code. |
| 40 | In the CI/CD for ML Pipelines pipeline, what happens next? On merge to main: full training on the real snapshot, with c... | On merge to main: full training on the real snapshot, with cached data and features. |
| 41 | In the CI/CD for ML Pipelines pipeline, what happens next? Run the evaluation suite on a frozen set; fail the build on ... | Run the evaluation suite on a frozen set; fail the build on a regression beyond epsilon. |
| 42 | In the CI/CD for ML Pipelines pipeline, what happens next? Register the artefact and deploy to shadow, not to productio... | Register the artefact and deploy to shadow, not to production. |
| 43 | In the CI/CD for ML Pipelines pipeline, what happens next? Promotion to production happens through the registry gate, o... | Promotion to production happens through the registry gate, outside CI. |
| 44 | Exercise focus: Fast pre-merge pipeline | Prove it catches the bugs that matter, fast. |
| 45 | Exercise focus: Smoke training that actually catches things | A real, tiny training run. |
| 46 | Exercise focus: Evaluation gate with derived epsilon | Make the gate meaningful. |
| 47 | Exercise focus: Cache design and validation | Content addressing, measured. |
| 48 | Exercise focus: Contract tests | Catch upstream breakage cheaply. |
| 49 | Exercise focus: Post-merge full pipeline | The slow half, done well. |
| 50 | State the Pre-merge time budget result for CI/CD for ML Pipelines. | build 90 s, unit 120 s, contracts 45 s, smoke 180 s = 7.25 min, acceptable. Adding full training (95 min) makes it 102 min, so full training moves post-merge and the pre-merge budget is preserved. |
| 51 | State the Regression gate result for CI/CD for ML Pipelines. | Baseline 0.912. Historical repeat-run sigma = 0.004, so epsilon = 3 sigma = 0.012. A candidate at 0.905 (delta -0.007) passes; 0.890 (-0.022) fails. |
| 52 | State the Cache validity result for CI/CD for ML Pipelines. | Commit changed but data version did not: key differs, so the data cache misses even though it could safely hit. Committing to per-stage keys (code, data, features) recovers the hit rate without risking staleness. |
| 53 | State the Pipeline duration as a metric result for CI/CD for ML Pipelines. | Full evaluation nightly: T_pipeline 95 min, queue 0 (fixed schedule) = detection up to 24h. Moving a smoke check pre-merge: T 7 min, queue ~0.05 min = detection in minutes. Total coverage is the union. |
| 54 | What is time-to-detect in CI? | Merge to alert. It is the number pipeline speed improves. |
| 55 | Why do ML pipelines get slower over time? | Uncached data and feature rebuilds, plus ever-growing evaluation suites. Cache and split them. |
| 56 | What belongs in the nightly suite? | Full training, full evaluation, drift checks, and the regression gate report. |
| 57 | How do you handle a hyperparameter change in CI? | Treat it like a model change: it needs the full evaluation suite, so it goes post-merge, not pre-merge. |
| 58 | Assumption / invariant to defend: Pre-merge pipeline finishes in minutes so people wait for it... | Pre-merge pipeline finishes in minutes so people wait for it |
| 59 | Assumption / invariant to defend: The evaluation set is frozen and versioned so deltas are comparable... | The evaluation set is frozen and versioned so deltas are comparable |
| 60 | Assumption / invariant to defend: Data and dependency caches are content-addressed, not time-based... | Data and dependency caches are content-addressed, not time-based |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
