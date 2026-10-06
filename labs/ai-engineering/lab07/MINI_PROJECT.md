# Lab 07: AI Testing & Evaluation — Mini Project

## Project: Evaluation Harness with Mutation Testing and Sampled Feedback

Build the evaluation system a production AI service needs: deterministic doubles,
golden sets, a runner with per-category reporting, statistical tooling, safety and
abstention suites, mutation testing, and a sampled offline feedback loop.

## Goal

A harness that catches a deliberate regression, produces honest confidence intervals,
and keeps its suite representative by feeding production failures back into it.

## Requirements

### Phase 1: Doubles and Fixtures
- [ ] `ScriptedLlmClient` (throws on exhaustion), `HashingEmbedder`, `SeededRng`,
      `FakeClock`.
- [ ] Verify two runs with the same seed produce identical output.
- [ ] 1,000 generated strings for round-trip tokenizer tests (unicode, emoji, empty).

### Phase 2: Golden Set
- [ ] 150 cases across 5 categories plus 30 unanswerable.
- [ ] Content hash; frozen semantics (edits require a new set).
- [ ] User-level split; near-duplicate detection across splits.

### Phase 3: Metric Implementations
- [ ] EM, token F1, BLEU-4, ROUGE-L, IoU; hand-verified to 1e-9.
- [ ] recall@k, MRR, nDCG with labelled retrieval cases.

### Phase 4: Runner and Reports
- [ ] Per-category accuracy, format validity, refusal, faithfulness, abstention.
- [ ] Deltas vs baseline with regression flags.
- [ ] `EvalConfig.key()` recorded on every report.

### Phase 5: Statistics
- [ ] Paired bootstrap; Wilson intervals; sample-size calculator.
- [ ] Verify a fake improvement is reported as within noise.
- [ ] Holm correction for a multi-variant sweep.

### Phase 6: Property and Fuzz Testing
- [ ] 10,000 generated inputs against the parser; zero uncaught exceptions.
- [ ] Global invariants: no nulls, bounded sizes, no PII, no empty chunks.
- [ ] Failure shrinking to a minimal reproducer.

### Phase 7: Mutation Testing
- [ ] 12 domain mutations (init, mask order, RRF, schema, sentinel, truncation order,
      clip ratio, normalization, top-p, ...).
- [ ] Report mutation score and survivors; add tests for survivors.

### Phase 8: Safety and Abstention
- [ ] Refusal, over-refusal, jailbreak, refusal consistency with a CI.
- [ ] Abstention: decline and false-decline rates plus `E[correct]`.

### Phase 9: Judge Calibration
- [ ] 50 hand-labelled items; agreement; attenuation factor.
- [ ] Simulate drift and show metrics stop being interpretable.

### Phase 10: Sampled Feedback Loop
- [ ] Sample production-like traffic with the documented strategy.
- [ ] Score offline; add failures to the golden set; measure coverage improvement.

### Phase 11: Flakiness and Performance
- [ ] 20 repeated runs; identify unstable tests; fix.
- [ ] Latency and token benchmarks with a regression check.

## Directory Layout

```
lab07/
  src/com/aiengineering/lab07/{doubles,suite,runner,stats,metrics,safety,quality,property,mutate,drift}/
  suite/golden_v1.jsonl
  suite/golden_v2.jsonl      (after the feedback loop)
  out/reports/*.json
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — doubles; determinism verified.
2. **M2** — golden set v1 with hash and user-level split.
3. **M3** — metrics hand-verified.
4. **M4** — runner produces per-category report with CIs.
5. **M5** — fake improvement reported as within noise.
6. **M6** — property suite; 10k inputs, zero uncaught exceptions.
7. **M7** — mutation score computed; survivors get tests.
8. **M8** — safety four-number report with a CI.
9. **M9** — abstention report with `E[correct]`.
10. **M10** — judge calibration and drift simulation.
11. **M11** — golden v2 built from sampled failures.
12. **M12** — flakiness zero; report written.

## Acceptance Criteria

- [ ] Two runs with the same seed are byte-identical.
- [ ] Golden edits impossible without a new set and hash.
- [ ] Split is user-level; near-duplicate check passes.
- [ ] All metrics match hand computations to 1e-9.
- [ ] Fake improvement reported as within noise with a stated CI.
- [ ] Zero uncaught exceptions over 10,000 fuzz inputs.
- [ ] Mutation score >= 0.85; survivors covered by new tests.
- [ ] All four safety numbers reported with a confidence interval.
- [ ] Abstention reports decline and false-decline separately.
- [ ] Judge drift demonstrably makes metrics uninterpretable.
- [ ] Golden v2 covers categories the sampled failures revealed.
- [ ] Zero flakiness in the blocking suite.

## Stretch Goals

- [ ] Differential testing between two pipeline versions.
- [ ] Fuzzing the agent loop for termination and budget compliance.
- [ ] Fairness regression suite with intersectional gaps.
- [ ] Golden set auto-refresh proposing new cases from traffic.
- [ ] Shadow evaluation at 100% traffic.
- [ ] Hypothesis-test-driven experiment decisions with multiple comparisons.
- [ ] Hypothesis shrinking for retrieval failures.
- [ ] Cost-of-evaluation tracked and optimized.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Flaky CI | Hidden clocks, hash ordering, shared state |
| Suite green, production bad | Golden set stale; no feedback loop |
| Eval scores too good | Split by query instead of user; contamination |
| Optimized the wrong metric | Metric gaming; no unrewarded proxy |
| Improvement inside noise | Unpaired comparison or too few items |
| Safety looks perfect | Decline-everything policy; no benign set |
| Mutation survivors | Missing invariant tests |
| Judge metrics drifting | Calibration not re-measured |
| Regression hidden | Aggregate-only reporting |
| Unbounded eval cost | Every run uses the full suite |

## Definition of Done

`REPORT.md` contains: the pyramid diagram, the deterministic-property table, the
golden set design with its hash and split, the metric verification results, a baseline
per-category report with CIs, one worked experiment with a "within noise" verdict, the
property and fuzz results, the mutation matrix with survivors and their new tests, the
safety and abstention reports, the judge calibration with the drift simulation, the
golden v2 diff, the flakiness audit, and a "which gate blocks a release and why"
conclusion.