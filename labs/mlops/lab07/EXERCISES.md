# CI/CD for ML Pipelines - Exercises

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

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab07
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out CiCdForMLPipelineLab
```

## Exercise 1: Fast pre-merge pipeline

**Task.** Prove it catches the bugs that matter, fast.

**Steps**
- Build a pipeline of compile, unit, contract and smoke stages.
- Add a smoke training run on a fixture.
- Break the feature transform and confirm fast failure.
- Measure total pre-merge time.

**Deliverable.** A pipeline that fails fast on broken feature code.

## Exercise 2: Smoke training that actually catches things

**Task.** A real, tiny training run.

**Steps**
- Use a 200-row fixture with a learnable signal.
- Assert training loss falls and accuracy beats 0.6.
- Break a feature and confirm the smoke run fails.
- Measure smoke runtime.

**Deliverable.** A smoke test that fails on broken features within minutes.

## Exercise 3: Evaluation gate with derived epsilon

**Task.** Make the gate meaningful.

**Steps**
- Freeze an eval set and version it.
- Run the baseline six times to measure variance.
- Derive epsilon and implement the gate.
- Show it passing a good model and failing a regressed one.

**Deliverable.** A gate with a defended epsilon and a demonstrated failure.

## Exercise 4: Cache design and validation

**Task.** Content addressing, measured.

**Steps**
- Implement per-stage content keys.
- Measure hit rates for code-only and data-only changes.
- Show stale serving is impossible.
- Report pipeline time with and without caching.

**Deliverable.** A cache hit-rate table and a time saving.

## Exercise 5: Contract tests

**Task.** Catch upstream breakage cheaply.

**Steps**
- Write schema contracts for 3 tables.
- Add a failing example per contract.
- Simulate an upstream type change.
- Confirm pre-merge catches it before training.

**Deliverable.** Contracts that fail on a simulated upstream change.

## Exercise 6: Post-merge full pipeline

**Task.** The slow half, done well.

**Steps**
- Run full training on the real snapshot post-merge.
- Report stage timings and queue time.
- Register the artefact and deploy to shadow.
- Prove CI does not promote to production.

**Deliverable.** A post-merge pipeline with a stage timing report.

## Exercise 7: Time-to-detect measurement

**Task.** Optimise the number that matters.

**Steps**
- Instrument detection time for each gate.
- Include queue time, not just runtime.
- Compare a nightly-only suite versus pre-merge plus nightly.
- Report the coverage-time trade-off.

**Deliverable.** A detection-time comparison.

## Exercise 8: Pipeline failure modes

**Task.** What happens when stages fail in CI.

**Steps**
- Fail each stage type and verify dependents stop.
- Verify cache is not written on failure.
- Verify retry is safe and idempotent.
- Write the pipeline failure runbook.

**Deliverable.** A runbook plus a test proving no partial cache writes.


---

## Self-Check Before You Move On

- [ ] My pre-merge pipeline is fast enough that people wait for it.
- [ ] My gate epsilon came from measured variance.
- [ ] My caches cannot serve stale content.
- [ ] CI does not promote to production.
