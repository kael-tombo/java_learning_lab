# CI/CD for ML Pipelines - Vision & Where This Is Going

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

## 1. The Future State

ML CI/CD converges on evaluation-as-code: versioned evaluation suites, data and model contracts, and continuous evaluation on shadow traffic so promotion criteria are computed rather than argued. Pipelines stay fast because the expensive half moves to scheduled and triggered jobs.

The test of that future state is boring: a new engineer ships a change to ci/cd for ml pipelines on day two without asking anyone where the magic lives.

## 2. What "Good" Looks Like in Practice

- Pre-merge is fast enough that engineers wait for it.
- Evaluation gates use a frozen, versioned set with variance-derived epsilons.
- Caches are content-addressed per stage.
- CI deploys to shadow; promotion lives in the registry gate.

## 3. Capability Ladder

| Level | Capability | You can... |
|---|---|---|
| L1 | Test | Unit tests and schema checks on every change. |
| L2 | Smoke | A tiny training run that catches broken feature code. |
| L3 | Gate | A frozen-set evaluation gate blocking regressions. |
| L4 | Evaluate continuously | Shadow evaluation and triggered full suites on promoted models. |

## 4. Behaviours to Build

Split fast from slow deliberately. Derive thresholds from measurement. Treat a bypassed gate as worse than no gate, and fix the pipeline rather than the policy.

## 5. Anti-Vision (the failure mode we are avoiding)

- Full training in pre-merge.
- Cache keys based on commit time.
- Gates with arbitrary epsilons that fire randomly.
- CI promoting to production because the build was green.

## 6. Technology Shifts That Change the Work

1. Evaluation suites as versioned code with per-slice regression gates.
1. Continuous evaluation on shadow traffic feeding automatic promotion criteria.
1. Data contracts and lineage checks as first-class CI stages.
1. Trigger-based rather than schedule-based expensive runs, keyed to data and model changes.

## 7. Your 30/60/90 Commitment

- **30 days.** Build a pre-merge pipeline with unit, contract and smoke stages under ten minutes.
- **60 days.** Add a frozen-set evaluation gate with an epsilon derived from repeat-run variance.
- **90 days.** Implement content-addressed per-stage caching and measure time-to-detect for both suites.

## 8. How To Tell You Are Actually Getting Better

- My pre-merge pipeline is fast enough that people wait for it.
- My gate epsilon came from measured variance.
- My caches cannot serve stale content.
- CI never promotes to production.

## 9. Principles That Should Not Change

- **Design CI stages for code, data, features** Design CI stages for code, data, features and model changes
- **Keep the pre-merge pipeline fast enough that people wait for it** Keep the pre-merge pipeline fast enough that people wait for it
- **Separate a fast smoke suite from a slow nightly evaluation suite** Separate a fast smoke suite from a slow nightly evaluation suite

> CI/CD for ML is the discipline of deciding what must be fast, what must be thorough, and refusing to trade one for the other.
