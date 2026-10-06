# MINI_PROJECT — Model Registry with Shadow Promotion and Rollback

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

**Brief.** Build a registry with atomic promotion, a declarative gate, shadow evaluation, and a rehearsed rollback you can time.

**Timebox.** 4 hours

## 1. Why This Project Exists

This is the control plane every ML team eventually needs, and the concurrency and rollback bugs are much cheaper to find here.

## 2. Requirements

- Immutable content-hashed versions with complete lineage (run, data version, commit).
- Atomic CAS promotion; demonstrate two concurrent promotions where exactly one wins.
- A declarative gate checking metrics, lineage, latency, fairness sign-off and artifact integrity.
- Shadow evaluation comparing challenger to champion on matured labels, with a minimum-mature threshold.
- Rollback through the same path, with the champion artifact cached locally.
- Retention sweeper that archives unreachable versions only.
- A timed rollback drill identifying whether the bottleneck is technical or human.

## 3. Build Order

| Step | Time | What you do | Done when |
|---|---|---|---|
| 1 | 30m | Registry core: versions, stages, hashes, lineage | Register and retrieve with hash verification |
| 2 | 30m | CAS promotion; force a race; assert exactly one wins | A race test that passes |
| 3 | 30m | Declarative gate returning all failure reasons | Readable refusals |
| 4 | 40m | Shadow evaluation with matured-label thresholds | A comparison that refuses to conclude early |
| 5 | 30m | Rollback through CAS with a local champion cache | One-command rollback |
| 6 | 30m | Retention sweeper respecting reachability | A preserved/deleted report |
| 7 | 30m | Timed rollback drill; pre-authorise and re-time | A drill report with the bottleneck |

## 4. Architecture Sketch

```text
 train -> artifact (content hash)
              |
        registry.register(version, lineage: run/dataVersion/commit)
              |
        deploy as shadow -> log (champion, challenger) predictions
              |
        mature labels -> ShadowEvaluator -> delta
              |
        PromotionGate (metrics, lineage, latency, fairness, hash)
              |
        CAS promote: expected=champion_vN -> challenger_vN+1
              |
        rollback(stage) -> previous champion (locally cached artifact)

  audit log: every transition with actor, expected, actual, gate reasons
```

## 5. Implementation Notes

- The race test is the point of the project; make it deterministic to run.
- Gate failures must name the failing check or people route around the gate.
- A shadow window shorter than label maturation produces confident nonsense.
- Cache the champion locally, then measure rollback with the artifact store unreachable.

## 6. Deliverables

1. Registry with CAS promotion and a passing concurrency test.
1. Gate with readable refusals for at least four distinct failures.
1. Shadow comparison enforcing a matured-label minimum.
1. Timed rollback drill report plus retention report.

## 7. Grading Rubric

| Dimension | Weight | What earns full marks |
|---|---|---|
| Correctness | 30% | CAS promotion, immutable versions, hash verification |
| Gate quality | 20% | Declarative checks with readable reasons, blocks a bad model |
| Evidence | 20% | Shadow evaluation with matured-label enforcement |
| Operations | 20% | Rollback timed, pre-authorised, artifact cached |
| Lifecycle | 10% | Retention respects reachability |

## 8. Stretch Goals

- Add per-environment gates with escalating strictness.
- Implement statistical promotion criteria (not just a fixed epsilon).
- Export the registry to a signed backup and prove restore.

## 9. Definition of Done

You are finished when every box below is checked, not when the code compiles.

- [ ] Immutable content-hashed versions with complete lineage (run, data version, commit).
- [ ] Atomic CAS promotion; demonstrate two concurrent promotions where exactly one wins.
- [ ] A declarative gate checking metrics, lineage, latency, fairness sign-off and artifact integrity.
- [ ] Shadow evaluation comparing challenger to champion on matured labels, with a minimum-mature threshold.
- [ ] Rollback through the same path, with the champion artifact cached locally.
- [ ] Retention sweeper that archives unreachable versions only.
- [ ] A stranger can reproduce the reported numbers with one command
- [ ] The limitations section says what this cannot do
- [ ] At least one number is alerted on in production

## 10. Retrospective Template

- What worked:
- What surprised me:
- The one number I would alert on in production:
- What I would delete before shipping this to real users:
